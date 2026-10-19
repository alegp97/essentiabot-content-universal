from urllib.parse import urlencode
from essentiabot_lib.services.http_stdlib import fetch_json
from essentiabot_lib.extractors.base import BaseExtractor, ExtractionResult
from essentiabot_lib.services.url_detector import video_id

class YouTubeExtractor(BaseExtractor):
    def extract(self, url):
        identifier = video_id(url)
        if not identifier:
            return self._failure(url, 'youtube', 'Could not extract a valid video ID.')
        transcript_error = ''
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            from requests import Session
            class TimedSession(Session):
                def request(self, *args, **kwargs):
                    kwargs.setdefault('timeout', 20)
                    return super().request(*args, **kwargs)
            with TimedSession() as session:
                transcripts = list(YouTubeTranscriptApi(http_client=session).list(identifier))
                ordered = sorted(transcripts, key=lambda t: (0 if t.language_code == 'es' else 1 if t.language_code == 'en' else 2, t.is_generated))
                for transcript in ordered:
                    try:
                        text = ' '.join(entry.text for entry in transcript.fetch())
                        if text.strip():
                            return ExtractionResult('youtube', url, text, {'video_id': identifier, 'language': transcript.language_code, 'is_generated': transcript.is_generated, 'method': 'transcript_api', 'content_scope': 'transcript'}).to_dict()
                    except Exception as exc:
                        transcript_error = type(exc).__name__
        except Exception as exc:
            transcript_error = type(exc).__name__
        try:
            import yt_dlp
            class SilentLogger:
                def debug(self, *args): pass
                def warning(self, *args): pass
                def error(self, *args): pass
            opts = {'quiet': True, 'no_warnings': True, 'skip_download': True, 'noplaylist': True, 'socket_timeout': 20, 'retries': 0, 'extractor_retries': 0, 'logger': SilentLogger()}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info('https://www.youtube.com/watch?v=' + identifier, download=False)
            info = info or {}
            title, description = info.get('title', ''), info.get('description', '')
            if not title and not description:
                raise ValueError('No useful metadata from yt-dlp')
            text = f"Title: {title}\nChannel: {info.get('uploader', '')}\n\nDescription:\n{description}"
            return ExtractionResult('youtube', url, text, {'video_id': identifier, 'method': 'yt_dlp_metadata', 'content_scope': 'metadata_only', 'transcript_error': transcript_error, 'limitation': 'No transcript was retrieved and the video was not viewed.'}).to_dict()
        except Exception as exc:
            metadata_error = type(exc).__name__
        try:
            item, status, _ = fetch_json('https://www.youtube.com/oembed?' + urlencode({'url': 'https://www.youtube.com/watch?v=' + identifier, 'format': 'json'}))
            title = str(item.get('title', '')).strip()
            if title:
                text = 'Title: ' + title + '\nChannel: ' + str(item.get('author_name', ''))
                return ExtractionResult('youtube', url, text, {'video_id': identifier, 'method': 'oembed_metadata', 'content_scope': 'metadata_only', 'http_status': status, 'transcript_error': transcript_error, 'metadata_error': metadata_error, 'limitation': 'No transcript was retrieved and the video was not viewed.'}).to_dict()
            return self._failure(url, 'youtube', 'No transcript or useful metadata was retrieved.')
        except Exception as exc:
            return self._failure(url, 'youtube', f'No transcript ({transcript_error or "empty"}) or metadata ({type(exc).__name__}).')
