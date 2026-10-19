"""Return compact evidence of a real extraction in the current environment."""
import argparse
import json
import logging
from pathlib import Path
import subprocess
import sys

def diagnose(url, install=False, env_file=None):
    command = [sys.executable, str(Path(__file__).resolve().with_name('run_essentiabot.py')), url]
    if env_file:
        command += ['--env-file', env_file]
    if install:
        command.append('--install')
    try:
        process = subprocess.run(command, capture_output=True, encoding='utf-8', errors='replace', timeout=300)
    except Exception as exc:
        return {'extractor_executed': 'not_confirmed', 'status': 'execution_failed', 'exception_type': type(exc).__name__}
    try:
        result = json.loads(process.stdout)
    except Exception:
        return {'extractor_executed': 'not_confirmed', 'status': 'no_valid_json', 'exit_code': process.returncode}
    meta = result.get('metadata', {})
    return {
        'extractor_executed': meta.get('execution', {}).get('extractor_executed', False),
        'execution': meta.get('execution', {}),
        'success': result.get('success', False),
        'source_type': result.get('source_type'),
        'method': meta.get('method'),
        'content_scope': meta.get('content_scope'),
        'text_characters': len(result.get('text', '')),
        'error_code': result.get('error_code'),
        'error_message': result.get('error_message', ''),
        'oembed_diagnostic': meta.get('oembed_diagnostic'),
        'login_error_type': meta.get('login_error_type'),
        'dependencies': meta.get('dependencies', {}),
        'dependency_resolution_order': meta.get('dependency_resolution_order', []),
        'exit_code': process.returncode,
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    parser.add_argument('--install', action='store_true')
    parser.add_argument('--env-file', help='Explicit private Instagram configuration file.')
    args = parser.parse_args()
    logging.disable(logging.CRITICAL)
    result = diagnose(args.url, args.install, args.env_file)
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result.get('success') else 2)
