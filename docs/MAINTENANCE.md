# Maintenance guide

## Architecture

`SKILL.md` controls agent decisions. `references/` documents source-specific execution and configuration. `agents/openai.yaml` is optional host metadata.

`run_essentiabot.py` validates and routes URLs, prepares optional dependencies, loads explicit configuration, downloads images when requested, and returns JSON. `bootstrap.py` resolves the session environment followed by an isolated cache. `diagnose.py` summarizes one actual extraction. `essentiabot_lib/extractors/` implements web, YouTube, and social extraction; `services/` handles HTTP, URL routing, and optional Instagram login.

Analysis belongs to the host assistant, not the Python process. There is no inference API, autonomous posting, audio transcription, or MCP service.

The Python library uses process-wide environment and client state for optional Instagram configuration. Use separate CLI processes for concurrent requests; the in-process `extract()` function is intended for serial calls, not threaded account isolation.

## Dependencies

The standard library is enough for web, TikTok, public Instagram metadata, image downloads, and diagnostics. Optional bootstrap profiles install `youtube-transcript-api>=1.2,<2` and `instagrapi>=2,<4`. These are compatibility ranges, not a reproducible lockfile. No third-party code is bundled. Existing yt-dlp, trafilatura, and BeautifulSoup are opportunistic enhancements and are not installed automatically.

Before releasing dependency updates, test the actual library interfaces and supported Python versions. Upstream Instagram authentication changes frequently. Relevant upstream documentation:

- [YouTube transcript API](https://github.com/jdepoix/youtube-transcript-api)
- [instagrapi](https://github.com/subzeroid/instagrapi)
- [instagrapi login migration](https://subzeroid.github.io/instagrapi/latest/usage-guide/login-migration/)

## Tests and release

Run `python -m unittest discover -s tests -v`. CI runs these deterministic tests on Windows, Ubuntu, and macOS using Python 3.10 and 3.13. A configured matrix is not evidence that remote CI has already passed.

Tests cover routing, failed-dependency metadata fallback, selected-slide handling, configuration isolation, HTML cleanup, JSON CLI behavior, and secret-free packaging. Network tests are intentionally separate from deterministic checks. Before claiming platform access, run real source diagnostics with permitted links in the current environment.

Update `skills/essentiabot-content/version.json` when releasing changes. Keep private env files and temporary images out of the repository and archives. Review provenance and rights before assigning a license. For reproducible deployments, create and maintain a reviewed lockfile for your chosen optional profiles.
