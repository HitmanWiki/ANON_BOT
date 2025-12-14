from web3 import Web3

BURN_ADDRESSES = [
    "0x0000000000000000000000000000000000000000",
    "0x000000000000000000000000000000000000dead",
]

KNOWN_LOCKERS = {
    "UNCX": "0x663A5C229c09b049E36dCc11a9B0d4a8Eb9db214",
    "TeamFinance": "0xE2fE530C047f2d85298b07D9333C05737f1435fB",
}

ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [{"name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
]


def lp_analysis(w3: Web3, pair_address: str):
    try:
        pair_address = Web3.to_checksum_address(pair_address)
        lp = w3.eth.contract(address=pair_address, abi=ERC20_ABI)

        total_supply = lp.functions.totalSupply().call()
        if total_supply == 0:
            return {
                "status": "burned",
                "burned_pct": 100.0,
                "source": "onchain",
            }

        burned = 0
        for addr in BURN_ADDRESSES:
            try:
                burned += lp.functions.balanceOf(
                    Web3.to_checksum_address(addr)
                ).call()
            except Exception:
                pass

        burned_pct = (burned / total_supply) * 100

        if burned_pct >= 95:
            return {
                "status": "burned",
                "burned_pct": round(burned_pct, 2),
                "source": "onchain",
            }

        # 🔒 Locker check
        for name, locker in KNOWN_LOCKERS.items():
            try:
                bal = lp.functions.balanceOf(
                    Web3.to_checksum_address(locker)
                ).call()
                if bal > 0:
                    return {
                        "status": "locked",
                        "locker": name,
                        "unlock_ts": None,
                        "source": "onchain",
                    }
            except Exception:
                pass

        return {"status": "unknown"}

    except Exception:
        return {"status": "unknown"}
