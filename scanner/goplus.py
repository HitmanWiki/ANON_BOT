import requests

GOPLUS_CHAINS = {
    "ETH": "1",
    "BSC": "56",
    "BASE": "8453",
}

GOPLUS_URL = "https://api.gopluslabs.io/api/v1/token_security/{}"


def fetch_goplus(chain: str, token: str):
    chain_id = GOPLUS_CHAINS.get(chain)
    if not chain_id:
        return None  # GoPlus does NOT support Monad

    try:
        r = requests.get(
            GOPLUS_URL.format(chain_id),
            params={"contract_addresses": token},
            timeout=8
        ).json()

        data = r.get("result", {}).get(token.lower())
        if not data:
            return None

        def flag(v): 
            return str(v) == "1"

        return {
            "honeypot": flag(data.get("is_honeypot")),
            "blacklist": flag(data.get("is_blacklisted")),
            "cannot_sell": flag(data.get("cannot_sell_all")),
            "cannot_buy": flag(data.get("cannot_buy")),
            "take_back_ownership": flag(data.get("can_take_back_ownership")),
            "hidden_owner": flag(data.get("hidden_owner")),
            "selfdestruct": flag(data.get("selfdestruct")),
            "proxy": flag(data.get("is_proxy")),
            "mintable": flag(data.get("is_mintable")),
            "open_source": flag(data.get("is_open_source")),
            "slippage_modifiable": flag(data.get("slippage_modifiable")),
            "personal_slippage_modifiable": flag(data.get("personal_slippage_modifiable")),
            "anti_whale": flag(data.get("anti_whale")),
            "anti_bot": flag(data.get("anti_bot")),
            "cooldown": flag(data.get("trading_cooldown")),
            "buy_tax": float(data.get("buy_tax", 0)),
            "sell_tax": float(data.get("sell_tax", 0)),
            "transfer_tax": float(data.get("transfer_tax", 0)),
        }

    except Exception:
        return None
