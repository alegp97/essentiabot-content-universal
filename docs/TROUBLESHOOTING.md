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

## Prompt and behavior problems

| Symptom | Cause to check | Remedy |
| --- | --- | --- |
| The agent says a named prompt does not exist | Wrong path or an older installed skill | Update the complete skill folder; consult its `prompts/README.md` |
| A prompt URL is echoed but not applied | The host could not read it, or confused it with the content source | Separate the behavioral-prompt URL from the content URL; paste the full prompt if needed |
| A bare URL produces the wrong format | A chat default was never established or a later instruction overrides it | State the desired lens in the message or set a chat default |
| Antithesis invents a second source | An analytical objection was presented as external evidence | Require it to be labeled as a constructed objection; request actual verification separately |
| A prompt seems to promise access to unavailable content | Prompt instructions cannot create tools | Supply the material or use a host with the necessary capabilities |
