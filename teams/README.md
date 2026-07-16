# Teams sideload (no AppSource)

You do **not** need store approval for a hackday demo.

## Prerequisites

1. Web app reachable over **HTTPS** (Teams blocks `http://localhost` in tabs).
2. Tenant allows **custom app sideloading** (ask admin early).

## HTTPS tunnel

With the web app on `http://localhost:3000`:

```bash
# Cloudflare Tunnel (example)
cloudflared tunnel --url http://localhost:3000

# or ngrok
ngrok http 3000
```

Copy the `https://….trycloudflare.com` (or ngrok) URL.

## Package the app

1. Edit [`manifest.json`](manifest.json):
   - Replace every `REPLACE_WITH_HTTPS_TUNNEL` with your HTTPS origin (no trailing slash).
   - Replace `REPLACE_WITH_HTTPS_TUNNEL_HOST` with the hostname only (e.g. `abc.trycloudflare.com`).
   - Optionally generate a new GUID for `"id"`.
2. Ensure `color.png` (192×192) and `outline.png` (32×32) are present.
3. Zip **contents** of `teams/` (manifest + icons), not the parent folder:

```bash
cd teams
zip -r ../acronym-atlas-teams.zip manifest.json color.png outline.png
```

## Sideload in Teams

1. Teams → **Apps** → **Manage your apps** → **Upload an app** → **Upload a custom app**
2. Select `acronym-atlas-teams.zip`
3. Open **Acronym Atlas** personal app → Lookup / Dictionary / Upload tabs

## Demo fallback

If sideloading is blocked: run the web app full-screen and show this manifest as the integration path (“same UI as a Teams personal tab”).

## Later (post-hackday)

- Messaging extension / message shortcut for “define selection”
- Bot Framework `@AcronymBot define SLA`
- AppSource submission
