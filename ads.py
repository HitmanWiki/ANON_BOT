import random
import time

ADS = [
    {
        "text": "🚀 Launch your token safely with XYZ Launchpad",
        "url": "https://xyzlaunch.io"
    },
    {
        "text": "📈 Track smart money with AlphaBot",
        "url": "https://t.me/alphabot"
    },
    {
        "text": "🛡️ Audit your contract before launch",
        "url": "https://auditpro.io"
    }
]

_last_seen = {}
COOLDOWN = 3600  # 1 hour per user


def get_ad(user_id):
    now = time.time()
    last = _last_seen.get(user_id, 0)

    if now - last < COOLDOWN:
        return None

    _last_seen[user_id] = now
    return random.choice(ADS)
