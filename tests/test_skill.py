"""Deterministic extraction and packaging checks; no account or network access."""
import contextlib
import importlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills' / 'essentiabot-content'
SCRIPTS = SKILL / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import run_essentiabot as runner
from essentiabot_lib.services.url_detector import classify_url, video_id
from essentiabot_lib.extractors.social_video import SocialVideoExtractor, _get_instagram_image_urls
from essentiabot_lib.extractors.web_page import WebPageExtractor
from essentiabot_lib.extractors.youtube import YouTubeExtractor
from essentiabot_lib import config


class SkillTests(unittest.TestCase):
    def test_url_boundaries(self):
        self.assertEqual(classify_url('https://youtube.com.evil.example/watch?v=abcdefghijk'), 'generic_web')
        self.assertEqual(classify_url('https://www.instagram.com/p/abc/'), 'instagram')
        for invalid in ('file:///etc/passwd', 'https://user:password@example.com'):
            with self.assertRaises(ValueError):
                classify_url(invalid)

    def test_youtube_identifiers(self):
        for url in ('https://youtu.be/abcdefghijk', 'https://www.youtube.com/shorts/abcdefghijk', 'https://www.youtube.com/watch?v=abcdefghijk'):
            self.assertEqual(video_id(url), 'abcdefghijk')
        self.assertIsNone(video_id('https://youtube.com/watch?v=short'))

    def test_invalid_url_is_json_failure(self):
        process = subprocess.run([sys.executable, str(SCRIPTS / 'run_essentiabot.py'), 'file:///secret'], capture_output=True, encoding='utf-8')
        self.assertEqual(process.returncode, 2)
        item = json.loads(process.stdout)
        self.assertEqual(item['error_code'], 'invalid_url')
        self.assertEqual(item['metadata']['execution']['skill_version'], '1.0.0')

    def test_explicit_env_parser(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'sample.env'
            path.write_text('# comment\nINSTAGRAM_USERNAME="sample-user"\nINSTAGRAM_PASSWORD=\nIGNORED=value\n', encoding='utf-8')
            self.assertEqual(runner.load_env_values(path), {'INSTAGRAM_USERNAME': 'sample-user', 'INSTAGRAM_PASSWORD': ''})

    def test_environment_restored_after_failure(self):
        original = {'INSTAGRAM_USERNAME': 'original-user', 'INSTAGRAM_PASSWORD': 'test-only-original'}
        def fail(*args, **kwargs):
            os.environ['INSTAGRAM_USERNAME'] = 'temporary-user'
            raise RuntimeError('simulated extraction failure')
        with patch.dict(os.environ, original), patch.object(runner, '_extract', side_effect=fail):
            with self.assertRaises(RuntimeError):
                runner.extract('https://example.com')
            self.assertEqual(os.environ['INSTAGRAM_USERNAME'], 'original-user')
            self.assertEqual(config.INSTAGRAM_USERNAME, 'original-user')
        config.refresh()

    def test_explicit_config_available_during_extraction_only(self):
        from essentiabot_lib.services.instagram_client import InstagramSession
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'sample.env'
            path.write_text('INSTAGRAM_USERNAME=sample-user\nINSTAGRAM_PASSWORD=test-only-value\n', encoding='utf-8')
            def social_extract(*args):
                self.assertEqual(config.INSTAGRAM_USERNAME, 'sample-user')
                self.assertEqual(config.INSTAGRAM_PASSWORD, 'test-only-value')
                return {'success': True, 'text': 'caption', 'metadata': {}, 'error_message': ''}
            with patch.dict(os.environ, {}, clear=True), patch.object(runner, 'initialize', return_value={'success': True}), patch.object(SocialVideoExtractor, 'extract', side_effect=social_extract):
                runner.extract('https://instagram.com/p/abc/', env_file=str(path))
                self.assertNotIn('INSTAGRAM_USERNAME', os.environ)
                self.assertEqual(config.INSTAGRAM_USERNAME, '')
                self.assertIsNone(InstagramSession._client)
        config.refresh()

    def test_public_instagram_without_credentials(self):
        html = '<meta property="og:description" content="A public post caption"><meta property="og:image" content="https://example.com/cover.jpg">'
        with patch.dict(os.environ, {}, clear=True), patch.object(runner, 'initialize', return_value={'success': True}), patch('essentiabot_lib.extractors.social_video.fetch_text', return_value=(html, {}, 200, 'https://instagram.com/p/abc/')):
            result = runner.extract('https://instagram.com/p/abc/')
        self.assertTrue(result['success'])
        self.assertEqual(result['metadata']['method'], 'public_html_metadata')

    def test_public_later_slide_not_misidentified(self):
        html = '<meta property="og:description" content="Whole post caption"><meta property="og:image" content="https://example.com/cover.jpg">'
        with patch('essentiabot_lib.extractors.social_video.fetch_text', return_value=(html, {}, 200, '')):
            result = SocialVideoExtractor()._try_instagram_public('https://instagram.com/p/abc/?img_index=2')
        self.assertTrue(result['success'])
        self.assertEqual(result['metadata']['requested_image_index'], 2)
        self.assertEqual(result['metadata']['image_urls'], [])

    def test_authenticated_slide_selection(self):
        from types import SimpleNamespace
        media = SimpleNamespace(thumbnail_url='cover', resources=[SimpleNamespace(thumbnail_url='one'), SimpleNamespace(thumbnail_url='two')])
        self.assertEqual(_get_instagram_image_urls(media, 2), ['two'])

    def test_social_limitation_is_preserved(self):
        social = {'success': True, 'text': 'caption', 'metadata': {'limitation': 'Selected slide unavailable.'}}
        with patch.object(runner, 'initialize', return_value={'success': True}), patch.object(SocialVideoExtractor, 'extract', return_value=social):
            result = runner.extract('https://instagram.com/p/abc/')
        self.assertIn('Selected slide unavailable.', result['metadata']['limitation'])

    def test_youtube_dependency_failure_still_allows_metadata(self):
        real_import = __import__
        def no_optional(name, *args, **kwargs):
            if name in {'youtube_transcript_api', 'yt_dlp'}:
                raise ImportError('optional module absent')
            return real_import(name, *args, **kwargs)
        with patch.object(runner, 'initialize', return_value={'success': False, 'error_message': 'dependencies absent'}), patch('builtins.__import__', side_effect=no_optional), patch('essentiabot_lib.extractors.youtube.fetch_json', return_value=({'title': 'Example video', 'author_name': 'Example creator'}, 200, '')):
            result = runner.extract('https://youtu.be/abcdefghijk')
        self.assertTrue(result['success'])
        self.assertEqual(result['metadata']['content_scope'], 'metadata_only')
        self.assertEqual(result['metadata']['method'], 'oembed_metadata')

    def test_web_cleanup(self):
        html = '<html><body><nav>Menu</nav><script>bad()</script><article><h1>Useful title</h1><p>' + ('Evidence and useful discussion. ' * 12) + '</p></article></body></html>'
        text = WebPageExtractor()._try_stdlib(html)
        self.assertIn('Useful title', text)
        self.assertNotIn('bad()', text)
        self.assertNotIn('Menu', text)

    def test_image_download_requires_supported_content_type(self):
        with patch.object(runner, 'fetch_bytes', return_value=(b'not an image', {'Content-Type': 'text/html'}, 200, 'https://example.com/x.png')):
            files, errors = runner.download_images(['https://example.com/x.png'])
        self.assertEqual(files, [])
        self.assertEqual(errors, ['ValueError'])

    def test_tiktok_caption_is_not_transcript(self):
        with patch('essentiabot_lib.extractors.social_video.fetch_json', return_value=({'title': 'Example caption', 'author_name': 'creator', 'thumbnail_url': 'https://example.com/cover.jpg'}, 200, '')):
            result = runner.extract('https://www.tiktok.com/@creator/video/123')
        self.assertTrue(result['success'])
        self.assertEqual(result['metadata']['content_scope'], 'caption_and_images_only')
        self.assertIn('not transcribed', result['metadata']['limitation'])

    def test_blank_template_and_no_private_resources(self):
        template = runner.load_env_values(SKILL / '.env.example')
        self.assertEqual(template, {'INSTAGRAM_USERNAME': '', 'INSTAGRAM_PASSWORD': ''})
        self.assertFalse(any(SKILL.rglob('instagram_private_config.txt')))
        self.assertFalse(any(SKILL.rglob('.env')))
        self.assertFalse((SCRIPTS / 'vendored').exists())

    def test_relative_markdown_links_resolve(self):
        import re
        for file in ROOT.rglob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)', file.read_text(encoding='utf-8')):
                if '://' in target or target.startswith('#'):
                    continue
                self.assertTrue((file.parent / target.split('#')[0]).exists(), f'{file}: {target}')


if __name__ == '__main__':
    unittest.main()
