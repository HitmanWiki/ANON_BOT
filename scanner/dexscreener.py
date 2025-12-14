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

        # Pick deepest liquidity pair
        pair = max(
            pairs,
            key=lambda p: float(p.get("liquidity", {}).get("usd", 0))
        )

        price = float(pair.get("priceUsd", 0))
        changes = pair.get("priceChange", {})
        vol = pair.get("volume", {})
        txns = pair.get("txns", {}).get("h24", {})

        # -------- LP STATUS (AUTHORITATIVE) --------
        lp_info = {
            "burned": bool(pair.get("liquidity", {}).get("burned")),
            "locked": bool(pair.get("liquidity", {}).get("locked")),
        }

        if lp_info["burned"]:
            lp_status = "burned"
        elif lp_info["locked"]:
            lp_status = "locked"
        else:
            lp_status = "unknown"

        # -------- SOCIALS + WEBSITE --------
        socials = {
            s.get("type"): s.get("url")
            for s in pair.get("info", {}).get("socials", [])
            if s.get("type") and s.get("url")
        }

        website = pair.get("info", {}).get("website")
        if website:
            socials["website"] = website

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
            "pair_created": pair.get("pairCreatedAt"),
            "pair_url": pair.get("url"),
            "lp": {
                "status": lp_status,      # burned | locked | unknown
                "burned": lp_info["burned"],
                "locked": lp_info["locked"],
            },
            "socials": socials,
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
