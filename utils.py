import time
RATE = {}
COOLDOWN = 10

def rate_limited(uid):
    now = time.time()
    if uid in RATE and now - RATE[uid] < COOLDOWN:
        return True
    RATE[uid] = now
    return False
