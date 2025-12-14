def verdict_engine(t):
    score = 100
    reasons = []

    # Core contract checks
    if not t.get("trading"):
        score -= 20
        reasons.append("Trading disabled")

    if t.get("owner") != "RENOUNCED":
        score -= 10
        reasons.append("Owner not renounced")

    # GoPlus security checks
    gp = t.get("goplus")
    if gp:
        if gp.get("honeypot"):
            score -= 40
            reasons.append("GoPlus: Honeypot detected")

        if gp.get("blacklisted"):
            score -= 25
            reasons.append("GoPlus: Blacklist detected")

        if gp.get("mintable"):
            score -= 10
            reasons.append("GoPlus: Mint function enabled")

        # ✅ Clean boost
        if (
            not gp.get("honeypot")
            and not gp.get("blacklisted")
            and gp.get("buy_tax", 100) <= 5
            and gp.get("sell_tax", 100) <= 5
        ):
            score += 10

    # Clamp score
    score = max(0, min(100, score))

    # Verdict tiers
    if score >= 75:
        verdict = "🟩🟩🟩 #GOOD 🟩🟩🟩"
        confidence = "High"
        risk_bar = "🟩🟩🟩"
        summary = "Low immediate risk detected"
    elif score >= 50:
        verdict = "🟡🟡🟡 #NEUTRAL 🟡🟡🟡"
        confidence = "Medium"
        risk_bar = "🟩🟩🟥"
        summary = "Moderate risk detected"
    else:
        verdict = "🟥🟥🟥 #RISKY 🟥🟥🟥"
        confidence = "Low"
        risk_bar = "🟥🟥🟥"
        summary = "High risk detected"

    return {
        "score": score,
        "verdict": verdict,
        "confidence": confidence,
        "risk_bar": risk_bar,
        "summary": summary,
        "reasons": reasons,
    }
