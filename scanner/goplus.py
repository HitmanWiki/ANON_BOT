import requests

CHAIN_IDS = {
    "ETH": 1,
    "BSC": 56,
    "BASE": 8453,
}

def fetch_goplus(chain: str, token: str):
    chain_id = CHAIN_IDS.get(chain.upper())
    if not chain_id:
        return None

    url = f"https://api.gopluslabs.io/api/v1/token_security/{chain_id}"
    try:
        r = requests.get(url, params={
            "contract_addresses": token
        }, timeout=10)
        j = r.json()
        data = j.get("result", {}).get(token.lower())
        if not data:
            return None

        return {
            "verified": True,
            "buy_tax": float(data.get("buy_tax", 0)),
            "sell_tax": float(data.get("sell_tax", 0)),
            "honeypot": data.get("is_honeypot") == "1",
            "blacklisted": data.get("is_blacklisted") == "1",
            "trading_paused": data.get("is_open_source") == "0",
            "mintable": data.get("is_mintable") == "1",
            "proxy": data.get("is_proxy") == "1",
        }
    except Exception:
        return None
