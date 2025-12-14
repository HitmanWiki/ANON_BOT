def verdict_engine(t, lp_info):
    score = 100
    reasons = []

    gp = t.get("goplus")
    if not gp:
        return {
            "label": "NEUTRAL",
            "score": 60,
            "confidence": "Medium",
            "reasons": ["GoPlus data unavailable"],
        }

    # 🚨 HARD FAILS
    if gp["honeypot"] or gp["cannot_sell"] or gp["cannot_buy"] or gp["blacklist"]:
        return {
            "label": "BAD",
            "score": 0,
            "confidence": "Low",
            "reasons": ["Critical GoPlus security flag detected"],
        }

    # ⚠️ HIGH RISK
    if gp["take_back_ownership"]:
        score -= 20
        reasons.append("Ownership reclaimable")
    if gp["hidden_owner"]:
        score -= 20
        reasons.append("Hidden owner detected")
    if gp["selfdestruct"]:
        score -= 25
        reasons.append("Self-destruct function present")
    if gp["mintable"]:
        score -= 15
        reasons.append("Minting enabled")
    if gp["proxy"]:
        score -= 10
        reasons.append("Proxy contract")

    # 💸 TAXES
    max_tax = max(gp["buy_tax"], gp["sell_tax"])
    if max_tax > 20:
        score -= 25
        reasons.append("Very high taxes")
    elif max_tax > 10:
        score -= 15
        reasons.append("High taxes")
    elif max_tax > 5:
        score -= 5
        reasons.append("Moderate taxes")

    if gp["transfer_tax"] > 0:
        score -= 5
        reasons.append("Transfer tax applied")

    # 🧩 MEDIUM
    if not gp["open_source"]:
        score -= 5
        reasons.append("Contract not open source")
    if gp["slippage_modifiable"]:
        score -= 10
        reasons.append("Slippage modifiable")
    if gp["personal_slippage_modifiable"]:
        score -= 5
        reasons.append("Per-user slippage control")
    if gp["anti_whale"]:
        score -= 3
    if gp["anti_bot"]:
        score -= 3
    if gp["cooldown"]:
        score -= 3

    # 🟡 LP uncertainty
    if lp_info["status"] == "unknown":
        score -= 10
        reasons.append("Liquidity lock unverifiable")

    # FINAL LABEL
    if score >= 85:
        label, conf = "GOOD", "High"
    elif score >= 65:
        label, conf = "NEUTRAL", "Medium"
    elif score >= 40:
        label, conf = "RISKY", "Low"
    else:
        label, conf = "BAD", "Low"

    return {
        "label": label,
        "score": max(score, 0),
        "confidence": conf,
        "reasons": reasons,
    }
