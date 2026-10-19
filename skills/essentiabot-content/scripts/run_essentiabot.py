"""Portable entrypoint. JSON results; no additional model API."""
from __future__ import annotations
import argparse
import hashlib
import json
import logging
import os
from pathlib import Path
import subprocess
import sys
import tempfile

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from bootstrap import activate
from essentiabot_lib.services.http_stdlib import fetch_bytes
from essentiabot_lib.services.url_detector import classify_url, hostname, is_image_url

def failure(url, source, message, code='extraction_failed'):
    return {'success': False, 'url': url, 'source_type': source, 'text': '', 'metadata': {}, 'error_code': code, 'error_message': message}

def attach_environment(result, prepared):
    result.setdefault('metadata', {})['dependencies'] = prepared.get('dependencies', {})
    result['metadata']['dependency_resolution_order'] = prepared.get('resolution_order', [])
    return result

def profiles_for(url, env_file=None):
    kind = classify_url(url)
    if is_image_url(url):
        profiles = ['image']
    elif kind == 'instagram' and not (env_file or (os.getenv('INSTAGRAM_USERNAME') and os.getenv('INSTAGRAM_PASSWORD'))):
        profiles = []
    else:
        profiles = [{'generic_web': 'web'}.get(kind, kind)]
    if env_file:
        profiles.append('env')
    return profiles

def initialize(profiles, install):
    if not profiles:
        return {'success': True}
    command = [sys.executable, str(SCRIPT_DIR / 'bootstrap.py')]
    for profile in profiles:
        command += ['--profile', profile]
    if install:
        command += ['--install']
    try:
        proc = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=220, env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
        return json.loads(proc.stdout)
    except Exception as exc:
        return {'success': False, 'error_message': 'Could not prepare Python: ' + type(exc).__name__}

def load_env_values(path):
    """Read the two supported Instagram settings without python-dotenv."""
    values = {}
    for raw_line in path.read_text(encoding='utf-8-sig').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        if line.startswith('export '):
            line = line[7:].lstrip()
        key, value = line.split('=', 1)
        key, value = key.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'\"', "'"}:
            value = value[1:-1]
        if key in {'INSTAGRAM_USERNAME', 'INSTAGRAM_PASSWORD'}:
            values[key] = value
    return values

def download_images(urls):
    folder = Path(tempfile.mkdtemp(prefix='essentiabot-images-'))
    paths, errors = [], []
    for url in urls[:4]:
        try:
            hostname(url)
            data, response_headers, _, _ = fetch_bytes(url, timeout=20)
            normalized_headers = {key.lower(): value for key, value in response_headers.items()}
            content_type = normalized_headers.get('content-type', '').split(';')[0].strip().lower()
            extensions = {'image/jpeg': '.jpg', 'image/png': '.png', 'image/webp': '.webp', 'image/gif': '.gif', 'image/bmp': '.bmp', 'image/tiff': '.tiff'}
            if content_type not in extensions:
                raise ValueError('The resource is not a supported image')
            if not data:
                raise ValueError('Empty image')
            path = folder / (hashlib.sha256(url.encode()).hexdigest()[:16] + extensions[content_type])
            path.write_bytes(data)
            paths.append(str(path))
        except Exception as exc:
            errors.append(type(exc).__name__)
    return paths, errors

def _extract(url, ocr=False, env_file=None, install=False):
    try:
        kind = classify_url(url)
        profiles = profiles_for(url, env_file)
    except ValueError as exc:
        return failure(url, 'unknown', str(exc), 'invalid_url')
    prepared = initialize(profiles, install)
    if not prepared.get('success') and kind not in {'instagram', 'youtube'}:
        result = failure(url, kind, prepared.get('error_message', 'Dependencies unavailable.'), 'environment_unavailable')
        result['metadata']['environment'] = prepared
        return result
    activate()
    if env_file:
        try:
            path = Path(env_file).expanduser()
            if not path.is_file():
                return attach_environment(failure(url, kind, 'The explicitly supplied configuration file does not exist.', 'configuration_missing'), prepared)
            values = load_env_values(path)
            for key in ('INSTAGRAM_USERNAME', 'INSTAGRAM_PASSWORD'):
                if values.get(key):
                    os.environ[key] = values[key]
        except Exception:
            return attach_environment(failure(url, kind, 'Could not read the supplied configuration.', 'configuration_error'), prepared)
    from essentiabot_lib import config
    config.refresh()
    try:
        if is_image_url(url):
            files, errors = download_images([url]) if ocr else ([], [])
            result = {'source_type': 'image', 'url': url, 'text': '', 'success': bool(files), 'error_message': '' if files else ('Could not download the image.' if ocr else 'Use --download-images to retrieve the image for visual inspection.'), 'metadata': {'image_urls': [url], 'image_files': files, 'download_errors': errors, 'content_scope': 'image_pending_vision', 'ocr_engine': 'current_conversation_model'}}
            return attach_environment(result, prepared)
        if kind == 'youtube':
            from essentiabot_lib.extractors.youtube import YouTubeExtractor
            result = YouTubeExtractor().extract(url)
        elif kind in {'instagram', 'tiktok'}:
            from essentiabot_lib.extractors.social_video import SocialVideoExtractor
            result = SocialVideoExtractor().extract(url)
            result['metadata']['content_scope'] = 'caption_and_images_only'
            result['metadata']['limitation'] = ' '.join(filter(None, [result['metadata'].get('limitation'), 'Audio was not transcribed and the full video was not viewed.']))
            if ocr and result['success']:
                files, errors = download_images(result['metadata'].get('image_urls', []))
                result['metadata'].update(image_files=files, download_errors=errors, ocr_engine='current_conversation_model')
        else:
            from essentiabot_lib.extractors.web_page import WebPageExtractor
            result = WebPageExtractor().extract(url)
            result['metadata']['content_scope'] = 'extracted_page_text'
        return attach_environment(result, prepared)
    except Exception as exc:
        return attach_environment(failure(url, kind, 'Extraction could not be completed: ' + type(exc).__name__), prepared)

def package_version():
    try:
        return json.loads((SCRIPT_DIR.parent / 'version.json').read_text(encoding='utf-8'))['version']
    except (OSError, ValueError, KeyError):
        return 'unknown'

def extract(url, ocr=False, env_file=None, install=False):
    # Keep credentials and client state scoped to one in-process extraction.
    from essentiabot_lib import config
    from essentiabot_lib.services.instagram_client import InstagramSession
    keys = ('INSTAGRAM_USERNAME', 'INSTAGRAM_PASSWORD')
    original = {key: os.environ.get(key) for key in keys}
    InstagramSession.reset()
    try:
        result = _extract(url, ocr, env_file, install)
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        config.refresh()
        InstagramSession.reset()
    result.setdefault('metadata', {})['execution'] = {
        'extractor_executed': True,
        'skill_version': package_version(),
        'python_version': sys.version.split()[0],
        'text_characters': len(result.get('text', '')),
    }
    return result

def main():
    parser = argparse.ArgumentParser(description='Extract available link content using this Python session.')
    parser.add_argument('url')
    parser.add_argument('--download-images', '--ocr', dest='ocr', action='store_true', help='Download images for visual inspection by the current host.')
    parser.add_argument('--env-file', help='Explicit file with optional Instagram configuration.')
    parser.add_argument('--install', action='store_true', help='Install missing dependencies into an isolated directory.')
    args = parser.parse_args()
    logging.disable(logging.CRITICAL)
    result = extract(args.url, args.ocr, args.env_file, args.install)
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['success'] else 2

if __name__ == '__main__':
    raise SystemExit(main())
