import time
from scanner.dexscreener import candle_color, trend_bias, vwap_ema_bias


def format_time_left(seconds):
    if seconds <= 0:
        return "Expired"
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    return f"{days}d {hours}h"


def format_report(t, verdict, market, lp_info, history):
    lines = []

    # ───────── TL;DR ─────────
    lines.append(f"🧾 Risk Summary: {verdict['summary']}\n")

    # ───────── Header ─────────
    lines.extend([
        f"• {t['name']} • ${t['symbol']} •",
        "🤖 ANON_AI_WATCHER • AI CODE CHECK",
        f"└{verdict['verdict']}",
    ])

    # ───────── Contract ─────────
    lines.extend([
        "",
        "🛡️ Contract",
        f"├ Ownership: {'🟢 Renounced' if t['owner']=='RENOUNCED' else '🔴 Not Renounced'}",
        f"├ Trading: {'🟢 Enabled' if t['trading'] else '🔴 Disabled'}",
    ])

    # ───────── Liquidity ─────────
    lines.append("")

    if lp_info["status"] == "burned":
        lines.append("🔥 Liquidity")
        lines.append("├ Status: 🟢 Burned")

        # Only show % if meaningful, otherwise explain burn
        if lp_info.get("burned_pct") is not None:
            lines.append(f"└ Burned: {lp_info['burned_pct']}%")
        else:
            lines.append("└ LP tokens sent to burn address")

    elif lp_info["status"] == "locked":
        lines.extend([
            "🔒 Liquidity",
            f"├ Status: 🟢 Locked ({lp_info.get('locker','Unknown')})",
            "└ Unlock time: Unknown",
        ])

    else:
        lines.extend([
            "⚠️ Liquidity",
            "└ Status: 🟡 Lock status unknown",
        ])


    # ───────── Trade Simulation ─────────
    lines.extend(["", "🧪 Trade Simulation"])
    gp = t.get("goplus")

    if gp:
        lines.extend([
            "🛡 Verified by GoPlus",
            f"└ Taxes: Buy {gp.get('buy_tax','N/A')}% | Sell {gp.get('sell_tax','N/A')}%",
        ])
    else:
        lines.extend([
            "├ Buy: 🟡 Likely OK (inferred)",
            "├ Sell: 🟡 Likely OK (inferred)",
            "└ Tax: N/A (external sim unavailable)",
        ])

    # ───────── Confidence ─────────
    lines.extend([
        "",
        f"{verdict['risk_bar']}  Confidence: {verdict['confidence']}",
        f"✨ Total Score: {verdict['score']}/100",
    ])

    # ───────── Reasons ─────────
    if verdict["reasons"]:
        lines.append("\n🚨 Reasons:")
        for r in verdict["reasons"]:
            lines.append(f"• {r}")

    # ───────── Advanced Analysis ─────────
    lines.append("\n🧠 Advanced Risk Analysis")
    adv = t.get("advanced_flags", [])
    if adv:
        for a in adv:
            lines.append(f"└ ⚠️ {a}")
    else:
        lines.extend([
            "└ 🟢 Distributed early buyers",
            "└ 🟢 No rug-pattern similarity",
            "└ 🟢 Stable liquidity ratio",
        ])

    # ───────── Risk Trend ─────────
    if history:
        delta = verdict["score"] - history["prev_score"]
        trend = "📈 Improving" if delta > 0 else "📉 Deteriorating" if delta < 0 else "➖ Stable"
        lines.extend([
            "",
            "📊 Risk Trend",
            f"└ {trend} ({history['prev_score']} → {verdict['score']})"
        ])

    # ───────── Market ─────────
    if market:
        pc = market["price_change"]
        lines.extend([
            "",
            "📈 Market",
            f"├ Price: ${market['price']:.8f}",
            f"├ MC: ${market['mc']:,}",
            f"├ Liq: ${market['liq']:,}",
            f"├ Buys / Sells (24h): {market['txns']['buys']} / {market['txns']['sells']}",
            f"├ Vol (24h): ${market['vol']['h24']:,}",
            f"├ Vol (6h):  ${market['vol']['h6']:,}",
            f"└ Vol (1h):  ${market['vol']['h1']:,}",
            "",
            "🕯️ Candle Summary",
            f"├ 5m:  {candle_color(pc['m5'])} {pc['m5']}%",
            f"├ 1h:  {candle_color(pc['h1'])} {pc['h1']}%",
            f"└ 24h: {candle_color(pc['h24'])} {pc['h24']}%",
            "",
            "🧠 Trend Bias",
            f"└ {trend_bias(pc)}",
            "",
            "📐 VWAP / EMA (Inference)",
            f"└ {vwap_ema_bias(market['price'], pc)}",
        ])

        socials = market.get("socials", {})
        if socials:
            lines.append("\n👥 Socials")
            for k, v in socials.items():
                lines.append(f"└ {k.upper()}: {v}")

    lines.extend([
        "",
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
