import time


BURN_ADDRESSES = {
    "0x0000000000000000000000000000000000000000",
    "0x000000000000000000000000000000000000dead",
}

KNOWN_LOCKERS = {
    "ETH": {
        "Team Finance": "0xE2fE530C047f2d85298b07D9333C05737f1435fB",
        "Unicrypt": "0x663A5C229c09b049E36dCc11a9B0d4a8Eb9db214",
        "PinkLock": "0x71B5759d73262FBb223956913ecF4ecC51057641",
    },
    "BSC": {
        "Team Finance": "0xE2fE530C047f2d85298b07D9333C05737f1435fB",
        "Unicrypt": "0xC765bddB93b0D1c1D330c6c7d62C7f0d3E0e0c6C",
        "PinkLock": "0x407993575c91ce7643a4d4cCACc9A98c36eE1BBE",
    },
    "BASE": {
        "Unicrypt": "0x663A5C229c09b049E36dCc11a9B0d4a8Eb9db214",
    },
}


def lp_analysis(w3, chain, lp_token, total_lp_supply):
    """
    Determines LP status:
    - burned
    - locked (known locker)
    - lock unknown
    """

    if not lp_token or not total_lp_supply:
        return {"status": "unknown"}

    # ───── 🔥 Burn detection ─────
    burned = 0
    for addr in BURN_ADDRESSES:
        try:
            bal = lp_token.functions.balanceOf(addr).call()
            burned += bal
        except Exception:
            continue

    if burned > 0:
        burned_pct = round((burned / total_lp_supply) * 100, 4)

        return {
            "status": "burned",
            "burned_pct": burned_pct,
            "burn_detected": True,
        }

    # ───── 🔒 Known locker detection ─────
    lockers = KNOWN_LOCKERS.get(chain, {})

    for name, locker_addr in lockers.items():
        try:
            bal = lp_token.functions.balanceOf(locker_addr).call()
            if bal > 0:
                return {
                    "status": "locked",
                    "locker": name,
                    "unlock_time": "View on locker site",
                }
        except Exception:
            continue

    # ───── 🟡 LP exists but locker unknown ─────
    return {
        "status": "unknown",
    }
