# Extraction and CLI reference

Run these commands from the skill directory using the actual Python executable in the session. Python 3.10+ is required. The helper returns JSON on stdout. Exit status `0` means material retrieved; `2` means failure. `--help` uses standard argparse output. Use a parent-process timeout for untrusted or slow sources.

```sh
python scripts/run_essentiabot.py "https://example.com"
python scripts/run_essentiabot.py "https://www.youtube.com/watch?v=VIDEO_ID" --install
python scripts/run_essentiabot.py "https://www.tiktok.com/@creator/video/VIDEO_ID" --download-images
python scripts/run_essentiabot.py "https://www.instagram.com/p/POST_CODE/?img_index=2" --download-images
python scripts/run_essentiabot.py "https://example.com/image.png" --download-images
python scripts/diagnose.py "https://example.com"
python scripts/bootstrap.py --profile web
python scripts/bootstrap.py --profile youtube --install
python scripts/bootstrap.py --profile instagram --install
```

Illustrative URLs containing `VIDEO_ID` or `POST_CODE` must be replaced. Valid YouTube IDs have 11 characters.

| Flag | Meaning |
| --- | --- |
| `--download-images` | Download up to four image URLs for host vision |
| `--ocr` | Compatibility alias for `--download-images`; does not run OCR |
| `--env-file PATH` | Read only the two documented Instagram settings from an explicit file |
| `--install` | Allow missing source dependencies to be installed into an isolated cache |

`diagnose.py` supports `--install` and `--env-file`. It reports execution, method, coverage, character count, errors, and dependencies, not the source text or configuration values.

## Source routes

- Web: returned HTML, with optional existing trafilatura or BeautifulSoup and a standard-library parser fallback. No browser rendering. Very short pages may be rejected as insufficient text. Returned content can still be a login or challenge page.
- YouTube: captions through optional `youtube-transcript-api`, preferring Spanish then English to preserve the original extractor's behavior; other languages follow. The transcript language does not dictate the analysis language. If captions fail, try existing optional yt-dlp metadata, then standard-library oEmbed. Metadata fallback remains available if dependency setup fails. There is no audio transcription or video download.
- TikTok: public oEmbed caption and thumbnail only. Shortened URLs depend on the platform endpoint accepting them. If needed, use host browsing to resolve the URL.
- Instagram: public Open Graph metadata when no account is configured; optional authenticated library otherwise. Public metadata cannot verify a selected later carousel slide, so its image is withheld when `img_index > 1`. Public descriptions can be generic. Authenticated captions refer to the whole post. No audio transcript.
- Images: extensions identify image URLs; content type is checked on download. URLs without a recognizable image extension may require direct host browsing. Downloaded files are placed in the OS temporary directory and are not automatically deleted because the host needs to open them.

## JSON contract

Top-level fields: `success` (boolean), `url`, `source_type`, `text`, `metadata` (object), `error_message`; failures may add `error_code`. Metadata can contain `method`, `content_scope`, `limitation`, `image_urls`, `image_files`, dependency details, and `execution` with version and character count. Optional metadata fields vary by source; consumers must tolerate additional fields.

Common scopes are `transcript`, `metadata_only`, `extracted_page_text`, `caption_and_images_only`, and `image_pending_vision`. A successful download with empty text still requires visual inspection. The wrapper preserves more specific limitations from source extractors.

Only HTTP(S) URLs without embedded user credentials are accepted. Do not expose this local CLI as a public fetching service: it is not a network sandbox or SSRF-protected proxy. Standard-library requests have timeouts and size limits; optional libraries can make additional requests. No private files are discovered automatically.
