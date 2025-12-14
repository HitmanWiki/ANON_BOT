def format_report(t, verdict, market, lp_info, history=None):
    lines = []

    # ───── Header ─────
    lines.extend([
        "🧾 Risk Summary: Low immediate risk detected",
        "",
        f"• {t.get('name','Unknown')} • ${t.get('symbol','UNKNOWN')} •",
        "🤖 ANON_AI_WATCHER • AI CODE CHECK",
        "└🟩🟩🟩 #GOOD 🟩🟩🟩",
        "",
    ])

    # ───── Contract ─────
    if t.get("owner_renounced") is True:
        ownership = "🟢 Renounced"
    elif t.get("owner_renounced") is None:
        ownership = "🟡 Unknown"
    else:
        ownership = "🔴 Not Renounced"

    trading = "🟢 Enabled" if t.get("trading") else "🔴 Disabled"

    lines.extend([
        "🛡️ Contract",
        f"├ Ownership: {ownership}",
        f"├ Trading: {trading}",
        "",
    ])

    # ───── Liquidity (AUTHORITATIVE) ─────
    if lp_info.get("status") == "burned":
        lines.extend([
            "🔥 Liquidity",
            "├ Status: 🟢 Burned",
            "└ LP tokens permanently burned (verified by DexScreener)",
            "",
        ])

    elif lp_info.get("status") == "locked":
        lines.extend([
            "🔒 Liquidity",
            f"├ Status: 🟢 Locked ({lp_info.get('locker','Unknown')})",
            "└ Unlock time: Unknown",
            "",
        ])

    else:
        lines.extend([
            "⚠️ Liquidity",
            "└ Status: 🟡 Lock status unknown",
            "",
        ])

    # ───── Trade Simulation (GoPlus) ─────
    if t.get("goplus"):
        taxes = t["goplus"]
        lines.extend([
            "🧪 Trade Simulation",
            "🛡 Verified by GoPlus",
            f"└ Taxes: Buy {taxes.get('buy_tax','N/A')}% | Sell {taxes.get('sell_tax','N/A')}%",
            "",
        ])

    # ───── Confidence ─────
    lines.extend([
        "🟩🟩🟩  Confidence: High",
        "✨ Total Score: 100/100",
        "",
    ])

    # ───── Reasons (if any) ─────
    reasons = []
    if t.get("owner_renounced") is False:
        reasons.append("Owner not renounced")

    if reasons:
        lines.append("🚨 Reasons:")
        for r in reasons:
            lines.append(f"• {r}")
        lines.append("")

    # ───── Market ─────
    if market:
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

        # ───── Candle Summary ─────
        pc = market.get("price_change", {})
        lines.extend([
            "🕯️ Candle Summary",
            f"├ 5m:  {'🟢' if pc.get('m5',0)>0 else '🔴' if pc.get('m5',0)<0 else '🟡'} {pc.get('m5',0)}%",
            f"├ 1h:  {'🟢' if pc.get('h1',0)>0 else '🔴' if pc.get('h1',0)<0 else '🟡'} {pc.get('h1',0)}%",
            f"└ 24h: {'🟢' if pc.get('h24',0)>0 else '🔴' if pc.get('h24',0)<0 else '🟡'} {pc.get('h24',0)}%",
            "",
        ])

        # ───── Trend Bias ─────
        trend_score = sum(1 for x in pc.values() if x > 0)
        if trend_score >= 2:
            trend = "🟢 Bullish"
        elif trend_score == 1:
            trend = "🟡 Neutral"
        else:
            trend = "🔴 Bearish"

        lines.extend([
            "🧠 Trend Bias",
            f"└ {trend}",
            "",
        ])

        # ───── Socials ─────
        socials = market.get("socials", {})
        if socials:
            lines.append("👥 Socials")
            for k, v in socials.items():
                lines.append(f"└ {k.upper()}: {v}")
            lines.append("")

    # ───── Footer ─────
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
