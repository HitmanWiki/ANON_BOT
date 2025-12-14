import time

BURN_ADDRESSES = {
    "0x0000000000000000000000000000000000000000",
    "0x000000000000000000000000000000000000dead",
}

KNOWN_LOCKERS = {
    "Team Finance": "0xE2fE530C047f2d85298b07D9333C05737f1435fB",
    "Unicrypt": "0x663A5C229c09b049E36dCc11a9B0d4a8Eb9db214",
    "PinkLock": "0x71B5759d73262FBb223956913ecF4ecC51057641",
}


def lp_analysis(w3, lp_token, total_lp_supply):
    """
    Determines LP status:
    - burned
    - locked (known locker)
    - lock unknown
    """

    if not lp_token or not total_lp_supply:
        return {"status": "unknown"}

    # 🔥 Burn detection
    burned = 0
    for addr in BURN_ADDRESSES:
        try:
            bal = lp_token.functions.balanceOf(addr).call()
            burned += bal
        except Exception:
            pass

    if burned > 0:
        burned_pct = 0.0
        if total_lp_supply > 0:
            burned_pct = round((burned / total_lp_supply) * 100, 2)

        return {
            "status": "burned",
            "burned_pct": burned_pct if burned_pct >= 1 else None,
            "burn_detected": True,
        }

        

    # 🔒 Known locker detection
    for name, locker in KNOWN_LOCKERS.items():
        try:
            bal = lp_token.functions.balanceOf(locker).call()
            if bal > 0:
                return {
                    "status": "locked",
                    "locker": name,
                    "unlock_ts": None,  # requires locker ABI
                }
        except Exception:
            pass

    # 🟡 LP exists but locker unknown
    return {
        "status": "unknown",
    }
