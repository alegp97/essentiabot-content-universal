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

## Maintaining the prompt library and visuals

Keep canonical templates in `skills/essentiabot-content/prompts/` so standalone installations contain them. Each template has a stable ID, a version, a use case, and one self-contained copyable code block. Load only the selected template to avoid expanding context unnecessarily. Keep the catalog and user examples aligned with the actual filenames.

Review prompt behavior using representative cases: a full article, metadata-only video access, a chart with unreadable labels, a source containing embedded commands, and an explicit translation request. Check that the response preserves evidence boundaries, does not invent a counter-source, and honors the user's actual task. A prose review or illustrative sample is not an executed cross-host evaluation.

Visual assets in `assets/` belong to repository documentation. Retain text equivalents and descriptive alt text. Label mock examples and conceptual artwork clearly, and preserve the original status of user-provided screenshots. Record visual provenance in `INSPIRATION.md`.
