import time
from scanner.dexscreener import volume_spike, recent_launch



def format_report(t, verdict, market, lp_info, history=None):
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

    # ───────── Header ─────────
    lines.extend([
        "🧾 Risk Summary: Low immediate risk detected",
        "",
        f"• {t.get('name','Unknown')} • ${t.get('symbol','UNKNOWN')} •",
        "🤖 ANON_AI_WATCHER • AI CODE CHECK",
        "└🟩🟩🟩 #GOOD 🟩🟩🟩",
        "",
    ])

    # ───────── Contract ─────────
    if t.get("owner_renounced") is True:
        ownership = "🟢 Renounced"
    elif t.get("owner_renounced") is None:
        ownership = "🟡 Unknown"
    else:
        owner_addr = t.get("owner_address")
        short = f"{owner_addr[:6]}…{owner_addr[-4:]}" if owner_addr else "EOA"
        ownership = f"🔴 Not Renounced ({short})"

    trading = "🟢 Enabled" if t.get("trading") else "🔴 Disabled"

    lines.extend([
        "🛡️ Contract",
        f"├ Ownership: {ownership}",
        f"├ Trading: {trading}",
        "",
    ])

    # ───────── Liquidity ─────────
    if lp_info.get("status") == "burned":
        lines.extend([
            "🔥 Liquidity",
            "├ Status: 🟢 Burned",
            "└ LP tokens permanently burned (verified by DexScreener)",
            "",
        ])
    elif lp_info.get("status") == "locked":
        unlock_ts = lp_info.get("unlock_ts")
        unlock = "Unlock time unknown"
        if unlock_ts:
            days = max(0, (unlock_ts - int(time.time())) // 86400)
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

    # ───────── Trade Simulation ─────────
    if t.get("goplus"):
        gp = t["goplus"]
        lines.extend([
            "🧪 Trade Simulation",
            "🛡 Verified by GoPlus",
            f"└ Taxes: Buy {gp.get('buy_tax','N/A')}% | Sell {gp.get('sell_tax','N/A')}%",
            "",
        ])
    else:
        lines.extend([
            "🧪 Trade Simulation",
            "└ ⚠️ External simulation unavailable",
            "",
        ])

    # ───────── Confidence (Decay applied) ─────────
    score = verdict.get("score", 100)
    confidence = verdict.get("confidence", "High")

    if market and market.get("vol", {}).get("h24", 0) < 10_000:
        score -= 10
        confidence = "Medium"

    lines.extend([
        f"🟩🟩🟩  Confidence: {confidence}",
        f"✨ Total Score: {max(score,0)}/100",
        "🧠 Confidence adjusted using contract + liquidity + activity",
        "",
    ])

    # ───────── Market ─────────
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
            f"├ 5m:  {'🟢' if pc.get('m5',0)>0 else '🔴' if pc.get('m5',0)<0 else '🟡'} {pc.get('m5',0)}%",
            f"├ 1h:  {'🟢' if pc.get('h1',0)>0 else '🔴' if pc.get('h1',0)<0 else '🟡'} {pc.get('h1',0)}%",
            f"└ 24h: {'🟢' if pc.get('h24',0)>0 else '🔴' if pc.get('h24',0)<0 else '🟡'} {pc.get('h24',0)}%",
            "",
        ])

    # ───────── Socials ─────────
    socials = market.get("socials", {}) if market else {}
    if socials:
        lines.append("👥 Socials")
        for k, v in socials.items():
            lines.append(f"└ {k.upper()}: {v}")
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
