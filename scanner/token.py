ERC20_ABI = [
    {"name": "name", "type": "function", "inputs": [], "outputs": [{"type": "string"}]},
    {"name": "symbol", "type": "function", "inputs": [], "outputs": [{"type": "string"}]},
    {"name": "owner", "type": "function", "inputs": [], "outputs": [{"type": "address"}]}
]

ZERO = "0x0000000000000000000000000000000000000000"

def get_token_info(w3, ca):
    info = {"name": "Unknown", "symbol": "Unknown", "owner": "Unknown"}
    try:
        c = w3.eth.contract(address=ca, abi=ERC20_ABI)
        info["name"] = c.functions.name().call()
        info["symbol"] = c.functions.symbol().call()
        owner = c.functions.owner().call()
        info["owner"] = "RENOUNCED" if owner.lower() == ZERO else owner
    except:
        pass
    return info
