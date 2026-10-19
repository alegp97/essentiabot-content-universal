# Validation evidence

Release: 1.0.0. Validation date: 2026-10-19.

## Local checks

The release is validated on Windows with Python 3.13.15. All 16 deterministic tests pass. The skill frontmatter and naming pass the local skill validator. Tests cover URL validation, YouTube ID parsing, CLI JSON failure output, explicit env parsing, credential restoration, per-call configuration, public Instagram routing, selected carousel handling, preserved source limitations, metadata fallback when dependencies fail, HTML cleanup, image content-type rejection, TikTok coverage, blank templates, and relative documentation links.

Mocked network responses validate routing and coverage semantics; they do not prove live access to those platforms. No real Instagram account was used. Cross-host assistant import, macOS/Linux execution, and remote GitHub CI have not been executed as part of this delivery. The CI matrix is provided for subsequent repository runs.

## Live smoke checks

| Check | Observed result |
| --- | --- |
| `diagnose.py https://example.com` | Success; standard-library HTML parser; `extracted_page_text`; 171 characters |
| `bootstrap.py --profile youtube --install` | Success; youtube-transcript-api 1.2.4 installed in an isolated temporary cache |
| `diagnose.py https://www.youtube.com/watch?v=jNQXAC9IVRw` | Success; `transcript_api`; `transcript`; 217 characters |

These results establish only the specific requests made in this environment. No live TikTok, Instagram login, or image-vision check was performed.

## Packaging checks

The release archives exclude Python caches and bytecode, populated env files, original private configuration, and vendored dependencies. The blank `.env.example`, Git ignore rules, and repository CI files are included. Every relative Markdown documentation link resolves. The separate skill archive contains the complete skill directory; the repository archive also contains manuals, tests, provenance, and CI configuration.
