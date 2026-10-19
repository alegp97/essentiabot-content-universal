"""Prepare optional dependencies using the session or an isolated cache."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

SCRIPT_DIR = Path(__file__).resolve().parent

GROUPS = {
    'web': [],
    'youtube': [('youtube_transcript_api', 'youtube-transcript-api>=1.2,<2')],
    'image': [],
    'tiktok': [],
    'instagram': [('instagrapi', 'instagrapi>=2,<4')],
    'env': [],
}

DIST_NAMES = {
    'youtube_transcript_api': 'youtube-transcript-api',
    'yt_dlp': 'yt-dlp',
    'bs4': 'beautifulsoup4',
    'dotenv': 'python-dotenv',
}


def dependency_dir() -> Path:
    key = hashlib.sha256((sys.executable + sys.version + json.dumps(GROUPS, sort_keys=True)).encode()).hexdigest()[:16]
    return Path((os.environ.get('ESSENTIABOT_CACHE_DIR') or tempfile.gettempdir())) / ('essentiabot-' + key) / 'packages'


def activate() -> Path:
    """Resolve the session environment first, then the isolated pip cache."""
    cache = dependency_dir()
    if cache.is_dir() and str(cache) not in sys.path:
        sys.path.append(str(cache))
    importlib.invalidate_caches()
    return cache


def importable(module: str) -> bool:
    try:
        imported = importlib.import_module(module)
        if module == 'youtube_transcript_api':
            return hasattr(imported.YouTubeTranscriptApi, 'list')
        return True
    except Exception:
        return False


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _distribution_version(distribution: str, search_path: Path | None = None) -> str:
    normalized = distribution.lower().replace('_', '-').replace('.', '-')
    try:
        if search_path is not None:
            for item in importlib.metadata.distributions(path=[str(search_path)]):
                name = (item.metadata.get('Name') or '').lower().replace('_', '-').replace('.', '-')
                if name == normalized:
                    return item.version
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return 'unknown'


def dependency_details(modules: list[str]) -> dict:
    details = {}
    cache = dependency_dir().resolve()
    for module_name in modules:
        distribution = DIST_NAMES.get(module_name, module_name.replace('_', '-'))
        try:
            module = importlib.import_module(module_name)
            module_path = Path(module.__file__).resolve()
            if _is_relative_to(module_path, cache):
                source, search_path = 'pip_target_cache', cache
            else:
                source, search_path = 'session_environment', None
            if module_name == 'yt_dlp':
                from yt_dlp.version import __version__ as version
            else:
                version = _distribution_version(distribution, search_path)
            details[module_name] = {
                'distribution': distribution,
                'version': version,
                'source': source,
            }
        except Exception:
            details[module_name] = {
                'distribution': distribution,
                'version': 'unavailable',
                'source': 'unavailable',
            }
    return details


def prepare(profiles: list[str], install: bool = False) -> dict:
    if sys.version_info < (3, 10):
        return {'success': False, 'error_code': 'python_version', 'error_message': 'Python 3.10 or later is required.'}
    path = activate()
    requirements = dict(pair for name in profiles for pair in GROUPS[name])
    missing = [name for name in requirements if not importable(name)]
    attempted = False
    install_error = ''
    if missing and install:
        attempted = True
        try:
            path.mkdir(parents=True, exist_ok=True)
            proc = subprocess.run(
                [sys.executable, '-m', 'pip', '--disable-pip-version-check', 'install', '--no-input', '--quiet', '--retries', '0', '--timeout', '20', '--target', str(path), '--upgrade', *requirements.values()],
                capture_output=True, text=True, timeout=180,
            )
            if proc.returncode:
                install_error = 'Dependency installation failed; check pip, permissions, and PyPI access.'
        except subprocess.TimeoutExpired:
            install_error = 'Dependency preparation timed out.'
        except Exception as exc:
            install_error = 'Dependency preparation unavailable: ' + type(exc).__name__
        activate()
        missing = [name for name in requirements if not importable(name)]
    return {
        'success': not missing and not install_error,
        'python_version': sys.version.split()[0],
        'python_executable': sys.executable,
        'profiles': profiles,
        'missing_modules': missing,
        'installation_attempted': attempted,
        'dependency_directory': str(path),
        'resolution_order': ['session_environment', 'pip_target_cache'],
        'dependencies': dependency_details(list(requirements)),
        'network_status': 'not_tested; checked when requesting a source',
        'error_message': install_error or ('Missing dependencies; use --install if permitted by the environment.' if missing else ''),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', choices=GROUPS, action='append')
    parser.add_argument('--install', action='store_true')
    args = parser.parse_args()
    result = prepare(args.profile or ['web'], args.install)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['success'] else 2)
