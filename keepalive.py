"""
Render's free tier only keeps *Web Services* alive, and only while they
receive HTTP requests — it has no free "background worker" plan. This
bot has no real webpage, so this file exists purely to give Render
something to ping so the process doesn't get killed after 15 minutes
of silence.

Pair this with an external uptime pinger (e.g. UptimeRobot,
cron-job.org — both free) hitting your Render URL every 5-10 minutes.

This is a workaround, not a real fix — see the README for the
tradeoffs vs. a proper always-on VPS.
"""

import os
from aiohttp import web

PORT = int(os.getenv("PORT", 8080))


async def health(_request):
    return web.Response(text="Meow Music is alive.")


async def run_keepalive_server():
    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"[keepalive] HTTP server listening on 0.0.0.0:{PORT}")
