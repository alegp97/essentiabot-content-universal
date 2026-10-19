import logging
from html.parser import HTMLParser
from urllib.error import HTTPError

from essentiabot_lib.extractors.base import BaseExtractor, ExtractionResult
from essentiabot_lib.services.http_stdlib import fetch_text

logger = logging.getLogger(__name__)
_MIN_TEXT_LENGTH = 200


class _ReadableHTML(HTMLParser):
    SKIP = {'script', 'style', 'nav', 'footer', 'header', 'aside', 'form', 'noscript', 'svg'}
    BREAKS = {'p', 'div', 'main', 'article', 'section', 'li', 'h1', 'h2', 'h3', 'h4', 'br', 'tr'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in self.SKIP:
            self.depth += 1
        elif not self.depth and tag in self.BREAKS:
            self.parts.append('\n')

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in self.SKIP and self.depth:
            self.depth -= 1
        elif not self.depth and tag in self.BREAKS:
            self.parts.append('\n')

    def handle_data(self, data):
        if not self.depth and data.strip():
            self.parts.append(data.strip() + ' ')

    def text(self):
        lines = [' '.join(line.split()) for line in ''.join(self.parts).splitlines()]
        return '\n'.join(line for line in lines if line)


class WebPageExtractor(BaseExtractor):
    def extract(self, url: str) -> dict:
        try:
            html, _, _, _ = fetch_text(url, timeout=15)
        except HTTPError as exc:
            return self._failure(url, 'generic_web', f'HTTP error {exc.code}.')
        except Exception as exc:
            return self._failure(url, 'generic_web', 'Could not download the page: ' + type(exc).__name__)

        for method, extractor in (
            ('trafilatura', lambda: self._try_trafilatura(html, url)),
            ('beautifulsoup', lambda: self._try_beautifulsoup(html)),
            ('stdlib_html_parser', lambda: self._try_stdlib(html)),
        ):
            text = extractor()
            if text and len(text) > (100 if method != 'trafilatura' else _MIN_TEXT_LENGTH):
                return ExtractionResult(
                    source_type='generic_web', url=url, text=text,
                    metadata={'method': method},
                ).to_dict()
        return self._failure(url, 'generic_web', 'Could not extract enough readable text from the page.')

    def _try_trafilatura(self, html: str, url: str) -> str:
        try:
            import trafilatura
            return trafilatura.extract(
                html, url=url, include_comments=False, include_tables=True, no_fallback=False
            ) or ''
        except Exception:
            return ''

    def _try_beautifulsoup(self, html: str) -> str:
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']):
                tag.decompose()
            container = soup.find('main') or soup.find('article') or soup.find(id='content') or soup.body
            if not container:
                return ''
            return '\n'.join(
                line.strip() for line in container.get_text(separator='\n').splitlines() if line.strip()
            )
        except Exception:
            return ''

    def _try_stdlib(self, html: str) -> str:
        try:
            parser = _ReadableHTML()
            parser.feed(html)
            return parser.text()
        except Exception:
            return ''
