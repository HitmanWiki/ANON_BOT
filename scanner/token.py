from web3 import Web3

ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "owner",
        "outputs": [{"name": "", "type": "address"}],
        "type": "function",
    },
]

ZERO_ADDRESSES = {
    "0x0000000000000000000000000000000000000000",
    "0x000000000000000000000000000000000000dead",
}


def get_token_info(w3: Web3, token_address: str):
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(token_address),
        abi=ERC20_ABI
    )

    # Defaults
    name = "Unknown"
    symbol = "UNKNOWN"
    owner_renounced = None  # tri-state: True / False / None

    try:
        name = contract.functions.name().call()
    except Exception:
        pass

    try:
        symbol = contract.functions.symbol().call()
    except Exception:
        pass

    # Ownership detection (BEST-EFFORT, NEVER LIE)
    try:
        owner = contract.functions.owner().call()
        if owner.lower() in ZERO_ADDRESSES:
            owner_renounced = True
        else:
            owner_renounced = False
    except Exception:
        # owner() does not exist or reverted
        owner_renounced = None

    return {
        "name": name,
        "symbol": symbol,
        "owner_renounced": owner_renounced,
    }
