# late-night-yap lock bot

Locks the `late-night-yap` channel (no one can send messages) at 6:00 AM
and unlocks it at 10:50 PM, every day, in Eastern Time — DST-safe, no
manual UTC math required.

## 1. Create the Discord bot

1. Go to https://discord.com/developers/applications → **New Application**.
2. Go to the **Bot** tab → **Reset Token** → copy the token (keep it secret).
3. Under **OAuth2 → URL Generator**: check the `bot` scope, and under
   permissions check `Manage Roles`, `Manage Channels`, `View Channels`.
4. Open the generated URL and add the bot to your server.

## 2. Deploy to Railway

1. Push this folder to a new GitHub repo (Railway deploys from GitHub).
2. On https://railway.app → **New Project → Deploy from GitHub repo** →
   pick this repo.
3. Railway will detect Python automatically and read the `Procfile`.
4. In the Railway project → **Variables**, add:
   - `DISCORD_TOKEN` = the token from step 1
   - `CHANNEL_NAME` = `late-night-yap` (only needed if you ever rename it)
   - `TIMEZONE` = `America/New_York` (only needed if you ever want to change it)
5. Deploy. Check the **Deployments → Logs** tab — you should see
   `Logged in as ...` once it's running.

That's it — Railway keeps it running 24/7, and it'll fire at 6:00 AM and
10:50 PM Eastern every day, correctly adjusting for daylight saving on
its own.
