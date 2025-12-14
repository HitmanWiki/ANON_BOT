import time
from web3 import Web3

BURN_ADDRESSES = {
    Web3.to_checksum_address("0x0000000000000000000000000000000000000000"),
    Web3.to_checksum_address("0x000000000000000000000000000000000000dEaD"),
}

LOCKERS = {
    "ETH": {
        "UNCX": "0x663A5C229c09b049E36dCc11a9B0d4a8Eb9db214",
        "TeamFinance": "0xE2fE530C047f2d85298b07D9333C05737f1435fB",
    },
    "BSC": {
        "UNCX": "0xC765bddB93b0D1c1D330c6c7d62C7f0d3E0e0c6C",
        "PinkLock": "0x407993575c91ce7643a4d4cCACc9A98c36eE1BBE",
    },
}

ERC20_ABI = [
    {"name": "totalSupply", "outputs": [{"type": "uint256"}], "inputs": [], "stateMutability": "view", "type": "function"},
    {"name": "balanceOf", "outputs": [{"type": "uint256"}], "inputs": [{"type": "address"}], "stateMutability": "view", "type": "function"},
]


def analyze_lp(w3, chain, lp_address):
    if not lp_address:
        return {"status": "unknown"}

    lp = w3.eth.contract(address=lp_address, abi=ERC20_ABI)

    try:
        total_supply = lp.functions.totalSupply().call()
    except Exception:
        return {"status": "unknown"}

    burned = 0
    for addr in BURN_ADDRESSES:
        try:
            burned += lp.functions.balanceOf(addr).call()
        except Exception:
            pass

    if burned > 0 and total_supply > 0:
        pct = round((burned / total_supply) * 100, 2)
        return {
            "status": "burned",
            "burned_pct": pct,
        }

    # locker detection
    for name, locker in LOCKERS.get(chain, {}).items():
        try:
            bal = lp.functions.balanceOf(Web3.to_checksum_address(locker)).call()
            if bal > 0:
                return {
                    "status": "locked",
                    "locker": name,
                    "unlock_ts": None,  # ABI dependent
                }
        except Exception:
            pass

    return {"status": "present"}
