import requests
import time

DEX_URL = "https://api.dexscreener.com/latest/dex/tokens/{}"

_CACHE = {}
CACHE_TTL = 30  # seconds


def _get_cache(key):
    v = _CACHE.get(key)
    if not v:
        return None
    data, ts = v
    if time.time() - ts > CACHE_TTL:
        del _CACHE[key]
        return None
    return data


def _set_cache(key, data):
    _CACHE[key] = (data, time.time())


def fetch_dex_data(ca: str):
    cached = _get_cache(ca)
    if cached:
        return cached

    try:
        r = requests.get(DEX_URL.format(ca), timeout=8).json()
        pairs = r.get("pairs")
        if not pairs:
            return None

        pair = max(
            pairs,
            key=lambda p: float(p.get("liquidity", {}).get("usd", 0))
        )

        price = float(pair.get("priceUsd", 0))
        changes = pair.get("priceChange", {})
        vol = pair.get("volume", {})
        txns = pair.get("txns", {}).get("h24", {})

        liq_usd = float(pair.get("liquidity", {}).get("usd", 0))

        socials = {}
        info = pair.get("info", {})

        socials = {
            s["type"]: s["url"]
            for s in info.get("socials", [])
        }

        # Add websites
        websites = info.get("websites", [])
        if websites:
            socials["website"] = websites[0].get("url")

        


        result = {
        "price": price,
        "price_change": {
            "m5": float(changes.get("m5", 0)),
            "h1": float(changes.get("h1", 0)),
            "h24": float(changes.get("h24", 0)),
        },
        "mc": int(float(pair.get("fdv", 0))),
        "liq": int(float(pair.get("liquidity", {}).get("usd", 0))),
        "txns": {
            "buys": int(txns.get("buys", 0)),
            "sells": int(txns.get("sells", 0)),
        },
        "vol": {
            "h24": int(float(vol.get("h24", 0))),
            "h6": int(float(vol.get("h6", 0))),
            "h1": int(float(vol.get("h1", 0))),
        },

        # 🔥 REQUIRED FOR LP ANALYSIS
        "pair_address": pair.get("pairAddress"),
        "chain_id": pair.get("chainId"),

        "pair_created": pair.get("pairCreatedAt"),
        "dexs": pair.get("url"),
        "dext": pair.get("info", {}).get("dextools"),

        "socials": {
            s["type"]: s["url"]
            for s in pair.get("info", {}).get("socials", [])
        },
    }


        _set_cache(ca, result)
        return result

    except Exception:
        return None


# -------- Helpers --------

def volume_spike(vol: dict) -> bool:
    """
    True if 1h volume >= 35% of 24h volume
    """
    try:
        if not vol or vol.get("h24", 0) == 0:
            return False
        return vol.get("h1", 0) / vol.get("h24", 1) >= 0.35
    except Exception:
        return False


def recent_launch(pair_created_ms):
    """
    True if launched within last 24h
    """
    if not pair_created_ms:
        return False
    age_hours = (time.time() * 1000 - pair_created_ms) / 3_600_000
    return age_hours <= 24
