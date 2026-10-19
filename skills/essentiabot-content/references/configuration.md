# Configuration manual

The supplied `.env.example` is intentionally blank. There is no owner account, password, token, saved session, or inherited authorization.

## Instagram (optional)

Public Instagram metadata is tried without a login. For authenticated extraction, the current user must authorize use of their own account in the current task.

1. Copy `.env.example` to a private file such as `.env` outside a shared folder.
2. Fill `INSTAGRAM_USERNAME` and `INSTAGRAM_PASSWORD` locally in an editor. Do not paste them into chat.
3. Pass its real path explicitly:

```sh
python scripts/run_essentiabot.py "https://www.instagram.com/p/POST_CODE/" --env-file "/private/path/.env" --install --download-images
```

This command assumes the skill folder is the current directory. On Windows use a quoted Windows path, for example `"C:\private\essentiabot.env"`. `POST_CODE` is illustrative; replace it with the actual post code.

Only `INSTAGRAM_USERNAME` and `INSTAGRAM_PASSWORD` are read from `--env-file`. Blank lines and `#` comments are allowed. Values may be quoted. There is no shell expansion, variable interpolation, or automatic env discovery. An explicit non-empty value overrides the matching process value for this extraction only. Existing process variables are restored afterwards.

Alternatively, set these two process environment variables through the host's private environment settings. The helper does not save login sessions. A login challenge stops the authenticated attempt; complete any account challenge in Instagram itself. Never disable 2FA to make extraction work. The optional library uses an unofficial interface; availability can change.

## Cache location

`ESSENTIABOT_CACHE_DIR` is the only other supported setting. Set it as a **process environment variable**, not through `--env-file`. Leave it unset or empty to use the system temporary directory. The helper creates an interpreter-specific `essentiabot-.../packages` subdirectory there.

PowerShell:

```powershell
$env:ESSENTIABOT_CACHE_DIR = 'C:\private\essentiabot-cache'
```

macOS/Linux:

```sh
export ESSENTIABOT_CACHE_DIR="$PWD/.cache/essentiabot"
```

Do not invent API-key settings: no AI provider key, YouTube API key, TikTok token, or additional service configuration is consumed by these scripts. Proxy settings and certificates may be handled by the underlying runtime; they are not dedicated Essentiabot env-file options.

## Keeping configuration private

The repository ignores `.env` and `.env.*`, while retaining `.env.example`. An arbitrary filename such as `essentiabot.env` is not protected by those patterns: keep it outside the repository or add its exact name to your private ignore rules. Git ignore does not remove files already tracked. Review staged files before sharing a modified package.
