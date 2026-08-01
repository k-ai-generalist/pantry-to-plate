# 🍳 Pantry to Plate — Streamlit edition

An AI sous-chef: type in what you have at home, and Claude designs one dish around it —
with the ingredients it uses, the shortest possible shopping list, and step-by-step
instructions. Includes a "✦ Surprise me" mode for something more adventurous, and an
animated copper pot that cooks while Claude thinks.

## Run locally

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...      # your key from console.anthropic.com
streamlit run app.py
```

Or store the key in `.streamlit/secrets.toml`:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

If no key is configured, the app shows a password field in the sidebar so you can
paste one at runtime.

## Deploy to Streamlit Community Cloud (free)

1. Push this folder to a GitHub repository (`app.py`, `requirements.txt`).
2. Go to https://share.streamlit.io → **New app** → pick your repo, branch, and `app.py`.
3. In the app's **Settings → Secrets**, add:
   ```
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
4. Deploy. You'll get a public `*.streamlit.app` URL.

> ⚠️ Note on keys: with the secret set, every visitor's request bills **your** API key.
> For a public app, consider adding rate limiting or leaving the key unset so each
> visitor supplies their own in the sidebar.

## Add Google login (optional)

The app can require Google sign-in before anyone can use it. This uses Streamlit's
built-in `st.login()` (OIDC) — no extra auth library or hand-rolled OAuth code.

**1. Create OAuth credentials in Google Cloud**
- Go to https://console.cloud.google.com/apis/credentials → **Create credentials → OAuth client ID**
- Application type: **Web application**
- Authorized redirect URIs:
  - `http://localhost:8501/oauth2callback` (local dev)
  - `https://YOUR-APP-NAME.streamlit.app/oauth2callback` (once deployed)
- Copy the generated **Client ID** and **Client secret**

**2. Add an `[auth]` block to secrets**

Local (`.streamlit/secrets.toml`):
```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "a-long-random-string-you-generate-yourself"

[auth.google]
client_id = "xxxxxxxx.apps.googleusercontent.com"
client_secret = "xxxxxxxx"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

Deployed (Streamlit Cloud → app **Settings → Secrets**): paste the same block, but
update `redirect_uri` to your deployed URL's `/oauth2callback` path.

Generate a strong `cookie_secret` with:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**3. That's it.** With `[auth]` present in secrets, the app shows a "Continue with
Google" screen and blocks everything else until the person signs in. Remove or
comment out the `[auth]` block to go back to running with no login at all — the app
detects its absence automatically.

Signed-in name, email, and avatar appear in the sidebar with a **Log out** button.
Streamlit only reads identity info (name/email/picture) from Google — it can't act
on the person's Google account or read their Gmail.

## Files

| File | Purpose |
|---|---|
| `app.py` | The whole app — UI, animated pot, Google login gate, and the Claude API call |
| `requirements.txt` | `streamlit`, `anthropic`, `Authlib` (needed by `st.login`) |

## How it works

- Ingredients live in `st.session_state`; chips are Streamlit buttons restyled as pills (click to remove).
- Pressing **Cook** swaps the pot into its "cooking" state (roaring flames, rattling lid,
  bubbles) inside an `st.empty()` placeholder while the blocking API call runs, then plays
  the lid-lift reveal before rendering the recipe card.
- **Surprise me** uses a different prompt *and* tints the flames violet-teal.
- Claude is asked to reply in strict JSON, which is parsed into the styled recipe card.
