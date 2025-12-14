def trading_enabled(contract_flag, market):
    # Strong inference from market activity
    if market:
        if market["liq"] > 0 and market["vol"]["h24"] > 0:
            return True

    # Fallback to contract flag (if explicitly disabled)
    if contract_flag is False:
        return False

    return True
