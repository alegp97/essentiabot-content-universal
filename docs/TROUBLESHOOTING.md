# Troubleshooting

| Symptom | Check | Next step |
| --- | --- | --- |
| Skill not discovered | Is the complete folder in the host's skills directory? | Refresh discovery; use instructions manually if import is unsupported |
| Python unavailable or files not mounted | Host capabilities | Browse the exact URL or use supplied content; do not invent execution |
| Missing dependencies | Run bootstrap for the specific profile | Add `--install` if permitted, or use metadata/public fallback |
| YouTube returns only a title | Read `content_scope` and `transcript_error` | Limit analysis or supply captions; this does not prove captions do not exist |
| Instagram login fails | Read the exception type in metadata | Stop authenticated attempts; check the account directly in Instagram |
| Later carousel image unavailable | Read `requested_image_index` and limitations | Supply that slide or use authorized authenticated extraction |
| Empty or generic page | Inspect returned text and coverage | Use host browsing; do not treat a login screen as an article |
| Timeout / HTTP 403 | Inspect actual diagnostic | Report the specific timeout/rejection, not a universal platform block |
| Downloaded image but no visual analysis | Does the host support vision? | Open it with host vision or disclose that it was not inspected |
| Non-ASCII text looks wrong | Use UTF-8 when saving or reading stdout | The helper emits UTF-8 JSON |

From the repository root:

```sh
python skills/essentiabot-content/scripts/diagnose.py "https://example.com"
```

For a private Instagram configuration, add `--env-file` with its actual path; add `--install` only when needed. Diagnostics omit text and credential values, but source URLs can contain private identifiers; review before sharing.
