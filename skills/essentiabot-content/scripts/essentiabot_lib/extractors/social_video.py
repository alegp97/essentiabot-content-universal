import logging
import re
import socket
from html import unescape
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, parse_qs, urlencode

from essentiabot_lib.services.url_detector import classify_url
from essentiabot_lib.services.http_stdlib import fetch_json, fetch_text

from essentiabot_lib import config
from essentiabot_lib.extractors.base import BaseExtractor, ExtractionResult

logger = logging.getLogger(__name__)

_INSTAGRAM_SHORTCODE_RE = re.compile(
    r"instagram\.com/(?:p|reel|tv)/([A-Za-z0-9_-]+)", re.IGNORECASE
)


class SocialVideoExtractor(BaseExtractor):
    """Retrieve social captions and image URLs, never video audio."""

    def extract(self, url: str) -> dict:
        source_type = self._detect_platform(url)

        if source_type == "instagram":
            return self._extract_instagram(url)
        if source_type == "tiktok":
            return self._extract_tiktok(url)

        return self._failure(url, source_type, "Unrecognized social platform.")

    # ------------------------------------------------------------------ Instagram

    def _extract_instagram(self, url: str) -> dict:
        authenticated_result = None
        if config.INSTAGRAM_USERNAME and config.INSTAGRAM_PASSWORD:
            authenticated_result = self._try_instagrapi(url)
            if authenticated_result.get('success'):
                return authenticated_result

        public_result = self._try_instagram_public(url)
        if public_result.get('success'):
            if authenticated_result:
                public_result['metadata']['authenticated_fallback_reason'] = authenticated_result.get('error_code')
            return public_result

        if authenticated_result:
            authenticated_result['metadata']['public_fallback'] = public_result.get('metadata', {}).get('public_diagnostic', {})
            return authenticated_result

        return public_result

    def _try_instagram_public(self, url: str) -> dict:
        try:
            html, _, status, _ = fetch_text(url, timeout=15)
            parser = _MetaParser()
            parser.feed(html)
            description = unescape(parser.values.get('og:description', '')).strip()
            title = unescape(parser.values.get('og:title', '')).strip()
            image = parser.values.get('og:image', '').strip()
            text = description or title
            if not text and not image:
                result = self._failure(url, 'instagram', 'The public page returned no usable content.')
                result['metadata']['public_diagnostic'] = {'status': 'empty_public_page', 'http_status': status}
                return result
            raw_index = parse_qs(urlsplit(url).query).get('img_index', [None])[0]
            if raw_index is not None and (not raw_index.isdigit() or int(raw_index) < 1):
                return self._failure(url, 'instagram', 'img_index must be a positive integer.')
            requested_index = int(raw_index) if raw_index is not None else None
            if requested_index is not None and requested_index > 1:
                image = ''  # Public metadata cannot verify the requested later slide.
            return ExtractionResult(
                source_type='instagram', url=url, text=text,
                metadata={
                    'method': 'public_html_metadata',
                    'image_urls': [image] if image else [],
                    'requested_image_index': requested_index,
                    'caption_scope': 'whole_post',
                    'public_diagnostic': {'status': 'content_retrieved', 'http_status': status},
                    'limitation': 'Public metadata does not verify a selected later carousel image; only the preview text and any verified cover are available.',
                },
                success=True,
            ).to_dict()
        except HTTPError as exc:
            result = self._failure(url, 'instagram', f'The public page returned HTTP {exc.code}.')
            result['metadata']['public_diagnostic'] = {'status': 'http_error', 'http_status': exc.code}
            return result
        except Exception as exc:
            result = self._failure(url, 'instagram', 'Could not read the public page: ' + type(exc).__name__)
            result['metadata']['public_diagnostic'] = {'status': 'public_fetch_error', 'exception_type': type(exc).__name__}
            return result

    def _try_instagrapi(self, url: str) -> dict:
        from essentiabot_lib.services.instagram_client import InstagramSession

        client = InstagramSession.get_client()
        if client is None:
            result = self._failure(
                url,
                "instagram",
                "Could not log in to Instagram.",
            )
            result['error_code'] = 'instagram_login_failed'
            result['metadata']['login_error_type'] = InstagramSession.last_error
            return result

        shortcode = _extract_instagram_shortcode(url)
        if not shortcode:
            return self._failure(
                url, "instagram", "Could not extract an Instagram shortcode from the URL."
            )

        try:
            media_pk = client.media_pk_from_code(shortcode)
            media = client.media_info(media_pk)
        except Exception as e:
            logger.error("Instagram media retrieval failed: %s", type(e).__name__)
            InstagramSession.reset()
            return self._failure(url, "instagram", f"Post access failed: {type(e).__name__}")

        text_parts: list[str] = []
        username = ""

        try:
            username = media.user.username
            text_parts.append(f"Author: @{username}")
        except Exception:
            pass

        caption = getattr(media, "caption_text", "") or ""
        if caption:
            text_parts.append(f"Caption:\n{caption}")

        location = getattr(media, "location", None)
        if location and hasattr(location, "name") and location.name:
            text_parts.append(f"Location: {location.name}")

        raw_index = parse_qs(urlsplit(url).query).get('img_index', [None])[0]
        try:
            requested_index = int(raw_index) if raw_index is not None else None
        except ValueError:
            return self._failure(url, 'instagram', 'img_index must be a positive integer.')
        if requested_index is not None and requested_index < 1:
            return self._failure(url, 'instagram', 'img_index must be a positive integer.')
        resources = getattr(media, 'resources', None) or []
        if requested_index is not None and requested_index > (len(resources) if resources else 1):
            return self._failure(url, 'instagram', 'The requested position does not exist in the retrieved content.')
        image_urls = _get_instagram_image_urls(media, requested_index)

        return ExtractionResult(
            source_type="instagram",
            url=url,
            text="\n\n".join(text_parts),
            metadata={
                "shortcode": shortcode,
                "username": username,
                "media_type": str(getattr(media, "media_type", "unknown")),
                "method": "instagrapi",
                "image_urls": image_urls,
                "requested_image_index": requested_index,
                "caption_scope": "whole_post",
            },
            success=True,
        ).to_dict()

    # ------------------------------------------------------------------ TikTok

    def _extract_tiktok(self, url: str) -> dict:
        caption, thumbnail_url, diagnostic = self._try_tiktok_oembed(url)

        if not caption and not thumbnail_url:
            result = self._failure(
                url,
                "tiktok",
                "No caption or thumbnail was retrieved through oEmbed. Read the diagnostic; this does not establish a general TikTok block.",
            )
            result['error_code'] = diagnostic['status']
            result['metadata']['oembed_diagnostic'] = diagnostic
            return result

        image_urls = [thumbnail_url] if thumbnail_url else []

        return ExtractionResult(
            source_type="tiktok",
            url=url,
            text=caption,
            metadata={"method": "oembed", "image_urls": image_urls, "oembed_diagnostic": diagnostic},
            success=True,
        ).to_dict()

    def _try_tiktok_oembed(self, url: str) -> tuple[str, str, dict]:
        """Record observed failures without inferring a platform-wide block."""
        oembed_url = "https://www.tiktok.com/oembed?" + urlencode({"url": url})
        try:
            data, status_code, _ = fetch_json(oembed_url, timeout=10)
            if status_code == 200:
                author = data.get("author_name", "").strip()
                title = data.get("title", "").strip()
                thumbnail = data.get("thumbnail_url", "").strip()

                caption = ""
                if title:
                    parts = [f"Author: @{author}"] if author else []
                    parts.append(f"Caption: {title}")
                    caption = "\n".join(parts)

                status = 'content_retrieved' if caption or thumbnail else 'empty_oembed_response'
                return caption, thumbnail, {'status': status, 'http_status': 200, 'api_error_code': data.get('error_code')}
            return '', '', {'status': 'oembed_http_error', 'http_status': status_code}
        except HTTPError as exc:
            return '', '', {'status': 'oembed_http_error', 'http_status': exc.code}
        except (TimeoutError, socket.timeout):
            return '', '', {'status': 'network_timeout'}
        except URLError as exc:
            return '', '', {'status': 'network_error', 'exception_type': type(exc.reason).__name__}
        except Exception as exc:
            return '', '', {'status': 'invalid_oembed_response', 'exception_type': type(exc).__name__}


    def _detect_platform(self, url: str) -> str:
        kind = classify_url(url)
        return kind if kind in {"instagram", "tiktok"} else "social_unknown"


# ------------------------------------------------------------------ Helpers

def _extract_instagram_shortcode(url: str) -> str | None:
    m = _INSTAGRAM_SHORTCODE_RE.search(url)
    return m.group(1) if m else None


class _MetaParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.values = {}

    def handle_starttag(self, tag, attrs):
        if tag.lower() != 'meta':
            return
        values = {str(key).lower(): value for key, value in attrs if value is not None}
        name = values.get('property') or values.get('name')
        content = values.get('content', '')
        if name and content and name.lower() not in self.values:
            self.values[name.lower()] = content


def _get_instagram_image_urls(media, requested_index=None) -> list[str]:
    """Get image URLs from an instagrapi media object."""
    urls: list[str] = []
    try:
        resources = getattr(media, 'resources', None) or []
        if requested_index is not None and resources:
            if 1 <= requested_index <= len(resources):
                selected = getattr(resources[requested_index - 1], 'thumbnail_url', None)
                return [str(selected)] if selected else []
            return []
        thumb = getattr(media, "thumbnail_url", None)
        if thumb:
            urls.append(str(thumb))

        resources = getattr(media, "resources", None) or []
        for resource in resources[:4]:
            t = getattr(resource, "thumbnail_url", None)
            if t and str(t) not in urls:
                urls.append(str(t))
    except Exception as e:
        logger.debug("Could not retrieve Instagram image URLs: %s", e)

    return urls
