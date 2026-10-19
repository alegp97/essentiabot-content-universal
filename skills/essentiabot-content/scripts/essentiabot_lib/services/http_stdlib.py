"""Small HTTP helpers that require only Python's standard library."""
from __future__ import annotations

import json
from urllib.request import Request, urlopen

from essentiabot_lib.services.url_detector import hostname

USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
)


def fetch_bytes(url: str, *, timeout: int = 20, max_bytes: int = 20 * 1024 * 1024,
                headers: dict | None = None) -> tuple[bytes, dict, int, str]:
    hostname(url)
    request_headers = {'User-Agent': USER_AGENT, 'Accept': '*/*'}
    if headers:
        request_headers.update(headers)
    request = Request(url, headers=request_headers)
    with urlopen(request, timeout=timeout) as response:
        final_url = response.geturl()
        hostname(final_url)
        data = response.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise ValueError('The response exceeds the allowed size.')
        return data, dict(response.headers.items()), response.status, final_url


def fetch_text(url: str, *, timeout: int = 20, max_bytes: int = 5 * 1024 * 1024,
               headers: dict | None = None) -> tuple[str, dict, int, str]:
    data, response_headers, status, final_url = fetch_bytes(
        url, timeout=timeout, max_bytes=max_bytes, headers=headers
    )
    content_type = response_headers.get('Content-Type', '')
    charset = 'utf-8'
    if 'charset=' in content_type.lower():
        charset = content_type.lower().split('charset=', 1)[1].split(';', 1)[0].strip()
    return data.decode(charset, errors='replace'), response_headers, status, final_url


def fetch_json(url: str, *, timeout: int = 20, max_bytes: int = 2 * 1024 * 1024,
               headers: dict | None = None) -> tuple[dict, int, str]:
    text, _, status, final_url = fetch_text(
        url, timeout=timeout, max_bytes=max_bytes, headers=headers
    )
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError('The JSON response is not an object.')
    return value, status, final_url
