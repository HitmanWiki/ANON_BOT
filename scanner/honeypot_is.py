import requests

API = "https://api.honeypot.is/v2/IsHoneypot"

CHAIN_IDS = {
    "ETH": 1,
    "BSC": 56,
    "BASE": 8453,
}

def check_honeypot_is(chain: str, ca: str):
    if chain not in CHAIN_IDS:
        return None

    try:
        r = requests.get(
            API,
            params={
                "address": ca,
                "chainID": CHAIN_IDS[chain]
            },
            timeout=8
        ).json()

        if not r.get("status"):
            return None

        res = r["result"]

        return {
            "can_buy": res.get("buySuccess"),
            "can_sell": res.get("sellSuccess"),
            "buy_tax": res.get("buyTax"),
            "sell_tax": res.get("sellTax"),
            "is_honeypot": res.get("isHoneypot"),
        }

    except:
        return None
