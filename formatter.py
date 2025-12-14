import time
from scanner.dexscreener import volume_spike, recent_launch


# ───────── Helpers ─────────

def verdict_bar(label: str) -> str:
    label = (label or "NEUTRAL").upper()
    if label == "GOOD":
        return "🟩🟩🟩 #GOOD 🟩🟩🟩"
    if label == "NEUTRAL":
        return "🟩🟩🟥 #NEUTRAL 🟥🟥🟥"
    if label == "RISKY":
        return "🟧🟧🟥 #RISKY 🟥🟥🟥"
    return "🟥🟥🟥 #BAD 🟥🟥🟥"


def candle_color(pct: float) -> str:
    if pct > 0:
        return "🟢"
    if pct < 0:
        return "🔴"
    return "🟡"


def trend_bias(pc: dict) -> str:
    score = 0
    if pc.get("m5", 0) > 0:
        score += 1
    if pc.get("h1", 0) > 0:
        score += 1
    if pc.get("h24", 0) > 0:
        score += 1

    if score >= 2:
        return "🟢 Bullish"
    if score == 1:
        return "🟡 Neutral"
    return "🔴 Bearish"


def vwap_ema_bias(pc: dict) -> str:
    if pc.get("m5", 0) > 0 and pc.get("h1", 0) > 0:
        return "🟢 Above VWAP / EMA (Bullish)"
    if pc.get("h24", 0) < -25:
        return "🔴 Extended / Below VWAP (Bearish)"
    return "🟡 Near VWAP / EMA"


# ───────── Main Formatter ─────────

def format_report(token: dict, verdict: dict, market: dict, lp_info: dict, history=None) -> str:
    lines = []

    # ───────── Badges ─────────
    badges = []
    if market:
        if volume_spike(market.get("vol", {})):
            badges.append("🔔 Unusual Volume Spike")
        if recent_launch(market.get("pair_created")):
            badges.append("🆕 Recently Launched")

    if badges:
        lines.append(" ".join(badges))
        lines.append("")

    # ───────── Header (DYNAMIC) ─────────
    label = verdict.get("label", "NEUTRAL")
    confidence = verdict.get("confidence", "Medium")

    lines.extend([
        f"🧾 Risk Summary: {confidence} immediate risk detected",
        "",
        f"• {token.get('name','Unknown')} • ${token.get('symbol','UNKNOWN')} •",
        "🤖 ANON_AI_WATCHER • AI CODE CHECK",
        f"└{verdict_bar(label)}",
        "",
    ])

    # ───────── Contract ─────────
    if token.get("owner_renounced") is True:
        ownership = "🟢 Renounced"
    elif token.get("owner_renounced") is False:
        owner = token.get("owner_address")
        short = f"{owner[:6]}…{owner[-4:]}" if owner else "EOA"
        ownership = f"🔴 Not Renounced ({short})"
    else:
        ownership = "🟡 Unknown"

    trading = "🟢 Enabled" if token.get("trading") else "🔴 Disabled"

    lines.extend([
        "🛡️ Contract",
        f"├ Ownership: {ownership}",
        f"├ Trading: {trading}",
        "",
    ])

    # ───────── Liquidity ─────────
    lp_status = lp_info.get("status")

    if lp_status == "burned":
        lines.extend([
            "🔥 Liquidity",
            "├ Status: 🟢 Burned",
            "└ LP tokens permanently burned (DexScreener verified)",
            "",
        ])
    elif lp_status == "locked":
        unlock = "Unlock time unknown"
        ts = lp_info.get("unlock_ts")
        if ts:
            days = max(0, (ts - int(time.time())) // 86400)
            unlock = f"{days} days remaining"

        lines.extend([
            "🔒 Liquidity",
            f"├ Status: 🟢 Locked ({lp_info.get('locker','Unknown')})",
            f"└ Unlock: {unlock}",
            "",
        ])
    else:
        lines.extend([
            "⚠️ Liquidity",
            "└ Status: 🟡 Lock status unknown",
            "",
        ])

    # ───────── Trade Simulation (GoPlus) ─────────
    goplus = token.get("goplus")
    if goplus:
        lines.extend([
            "🧪 Trade Simulation",
            "🛡 Verified by GoPlus",
            f"└ Taxes: Buy {goplus.get('buy_tax','N/A')}% | Sell {goplus.get('sell_tax','N/A')}%",
            "",
        ])
    else:
        lines.extend([
            "🧪 Trade Simulation",
            "└ ⚠️ External simulation unavailable",
            "",
        ])

    # ───────── Confidence & Score (FROM VERDICT) ─────────
    score = verdict.get("score", 0)

    lines.extend([
        f"🟩🟩🟩  Confidence: {confidence}",
        f"✨ Total Score: {score}/100",
        "🧠 Confidence derived from contract risk, liquidity certainty & market activity",
        "",
    ])

    reasons = verdict.get("reasons") or []
    if reasons:
        lines.append("🚨 Reasons:")
        for r in reasons:
            lines.append(f"• {r}")
        lines.append("")

    # ───────── Market (DexScreener) ─────────
    if market:
        pc = market.get("price_change", {})

        lines.extend([
            "📈 Market",
            f"├ Price: ${market.get('price',0):,.8f}",
            f"├ MC: ${market.get('mc',0):,}",
            f"├ Liq: ${market.get('liq',0):,}",
            f"├ Buys / Sells (24h): {market.get('txns',{}).get('buys',0)} / {market.get('txns',{}).get('sells',0)}",
            f"├ Vol (24h): ${market.get('vol',{}).get('h24',0):,}",
            f"├ Vol (6h):  ${market.get('vol',{}).get('h6',0):,}",
            f"└ Vol (1h):  ${market.get('vol',{}).get('h1',0):,}",
            "",
        ])

        lines.extend([
            "🕯️ Candle Summary",
            f"├ 5m:  {candle_color(pc.get('m5',0))} {pc.get('m5',0)}%",
            f"├ 1h:  {candle_color(pc.get('h1',0))} {pc.get('h1',0)}%",
            f"└ 24h: {candle_color(pc.get('h24',0))} {pc.get('h24',0)}%",
            "",
            "🧠 Trend Bias",
            f"└ {trend_bias(pc)}",
            "",
            "📐 VWAP / EMA (Inference)",
            f"└ {vwap_ema_bias(pc)}",
            "",
        ])

    # ───────── Socials (INCLUDING WEBSITE) ─────────
    socials = market.get("socials", {}) if market else {}
    if socials:
        lines.append("👥 Socials")
        if socials.get("twitter"):
            lines.append(f"└ TWITTER: {socials['twitter']}")
        if socials.get("telegram"):
            lines.append(f"└ TELEGRAM: {socials['telegram']}")
        if socials.get("website"):
            lines.append(f"└ WEBSITE: {socials['website']}")
        lines.append("")

    # ───────── Footer ─────────
    lines.extend([
        "━━━━━━━━━━━━",
        "📢 Place your ads here",
        "👉 Contact: @An0N55",
        "",
        "⚠️ Disclaimer",
        "This report is automated and for informational purposes only.",
        "Always DYOR before trading.",
        "━━━━━━━━━━━━",
    ])

    return "\n".join(lines)
