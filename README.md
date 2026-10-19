# Essentiabot Content — Universal Skill

A standalone skill for extracting accessible content and separating useful ideas from hype. All instructions, manuals, examples, and helper messages are in English. Analysis can be delivered in any language requested by the user.

This repository contains the skill at **`skills/essentiabot-content/`**. It does not require the original plugin, an MCP server, or an AI API key. Python helpers require Python 3.10+. Without Python, a compatible agent can follow the instructions using its own browsing tools or user-provided material.

Repository: [alegp97/essentiabot-content-universal](https://github.com/alegp97/essentiabot-content-universal).

“Universal” means portable instructions and cross-platform Python source, with graceful capability fallbacks. It does not mean every assistant supports automatic skill import, or that every source is accessible. No live cross-host compatibility certification is claimed.

## Start here

- [Installation and GitHub guide](docs/INSTALLATION.md)
- [User manual and examples](docs/USER_MANUAL.md)
- [Configuration and blank env template](skills/essentiabot-content/references/configuration.md)
- [Extraction and command reference](skills/essentiabot-content/references/extraction.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Technical maintenance guide](docs/MAINTENANCE.md)
- [Review of the original plugin and migration](docs/PLUGIN_REVIEW.md)
- [Validation evidence](docs/VALIDATION.md)

## Capabilities and limits

| Source | Available route | Actual coverage |
| --- | --- | --- |
| Websites | Standard-library HTML parser; optional existing trafilatura/BeautifulSoup | Returned page text; no JavaScript rendering |
| YouTube | Optional transcript library; optional existing yt-dlp; public oEmbed fallback | Captions if accessible; otherwise metadata only |
| TikTok | Public oEmbed | Caption and thumbnail; no audio transcript |
| Instagram | Public HTML metadata; optional user authentication | Preview metadata, or post caption and image URLs; no audio transcript |
| Images | Download plus host vision, or user attachment | Visual analysis only when actually opened by the host |

No private credentials, saved sessions, original plugin manifests, or bundled third-party packages are distributed. Optional dependencies are installed separately. The source plugin remains unchanged.

## Local check

From the repository root:

```sh
python -m unittest discover -s tests -v
python skills/essentiabot-content/scripts/bootstrap.py --profile web
python skills/essentiabot-content/scripts/run_essentiabot.py "https://example.com"
```

On systems where Python is named `python3`, substitute that command. See the installation guide for Windows and macOS/Linux paths.

## Provenance and licensing

Adapted from the owner's installed Essentiabot Content portable plugin 0.4.0. This repository preserves and adapts its extractor source. No open-source license has been assigned by this conversion: the rights holder must choose a license before granting public reuse rights. A public GitHub repository alone does not grant such rights. See [PROVENANCE.md](PROVENANCE.md).
