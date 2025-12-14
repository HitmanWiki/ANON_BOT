import requests

URL = "https://api.dexscreener.com/latest/dex/tokens/{}"


def fetch_dex_data(ca: str):
    try:
        r = requests.get(URL.format(ca), timeout=8)
        data = r.json()

        pairs = data.get("pairs")
        if not pairs:
            return None

        # Choose highest liquidity pair
        pair = max(
            pairs,
            key=lambda p: float(p.get("liquidity", {}).get("usd", 0))
        )

        price = float(pair.get("priceUsd", 0))
        changes = pair.get("priceChange", {}) or {}
        volume = pair.get("volume", {}) or {}
        txns_24h = pair.get("txns", {}).get("h24", {}) or {}

        # ───── LP burned detection (DexScreener) ─────
        lp_burned = False
        liquidity = pair.get("liquidity", {})
        if isinstance(liquidity, dict):
            lp_burned = liquidity.get("lpBurned", False)

        info = pair.get("info", {}) or {}
        if info.get("lpBurned") is True:
            lp_burned = True

        # ───── Socials + Website ─────
        socials = {
            s.get("type"): s.get("url")
            for s in info.get("socials", [])
            if s.get("url")
        }

        if info.get("website"):
            socials["website"] = info.get("website")

        if not socials.get("website"):
            websites = info.get("websites", [])
            if isinstance(websites, list) and websites:
                socials["website"] = websites[0].get("url")

        return {
            "price": price,
            "price_change": {
                "m5": float(changes.get("m5", 0)),
                "h1": float(changes.get("h1", 0)),
                "h24": float(changes.get("h24", 0)),
            },
            "mc": int(float(pair.get("fdv", 0))),
            "liq": int(float(pair.get("liquidity", {}).get("usd", 0))),
            "txns": {
                "buys": int(txns_24h.get("buys", 0)),
                "sells": int(txns_24h.get("sells", 0)),
            },
            "vol": {
                "h24": int(float(volume.get("h24", 0))),
                "h6": int(float(volume.get("h6", 0))),
                "h1": int(float(volume.get("h1", 0))),
            },
            "pair_address": pair.get("pairAddress"),
            "pair_created": pair.get("pairCreatedAt"),
            "dexs": pair.get("url"),
            "dext": info.get("dextools"),
            "socials": socials,
            "lp_burned": lp_burned,
        }

    except Exception:
        return None


# ───────── Helpers ─────────

def volume_spike(vol: dict) -> bool:
    """
    Detect unusual volume spike (1h vs 24h)
    """
    try:
        if not vol or vol.get("h24", 0) == 0:
            return False
        return vol.get("h1", 0) / vol.get("h24", 1) > 0.4
    except Exception:
        return False


def candle_color(pct: float) -> str:
    if pct > 0:
        return "🟢"
    if pct < 0:
        return "🔴"
    return "🟡"


def trend_bias(changes: dict) -> str:
    score = 0
    if changes.get("m5", 0) > 0:
        score += 1
    if changes.get("h1", 0) > 0:
        score += 1
    if changes.get("h24", 0) > 0:
        score += 1

    if score >= 2:
        return "🟢 Bullish"
    if score == 1:
        return "🟡 Neutral"
    return "🔴 Bearish"


def vwap_ema_bias(price: float, changes: dict) -> str:
    """
    Inference-based VWAP / EMA bias
    (DexScreener does not expose real VWAP/EMA)
    """
    score = 0

    # Short-term momentum
    if changes.get("m5", 0) > 0:
        score += 1
    if changes.get("h1", 0) > 0:
        score += 1

    # Overextension heuristic
    if changes.get("h24", 0) > 50:
        score -= 1

    if score >= 2:
        return "🟢 Above VWAP / EMA (Bullish)"
    if score == 1:
        return "🟡 Near VWAP / EMA"
    return "🔴 Below VWAP / EMA (Bearish)"
