from web3 import Web3

# Burn addresses
BURN_ADDRESSES = {
    Web3.to_checksum_address("0x0000000000000000000000000000000000000000"),
    Web3.to_checksum_address("0x000000000000000000000000000000000000dead"),
}

# Known LP lockers (multichain)
KNOWN_LOCKERS = {
    "Team Finance": Web3.to_checksum_address("0xE2fE530C047f2d85298b07D9333C05737f1435fB"),
    "Unicrypt": Web3.to_checksum_address("0x663A5C229c09b049E36dCc11a9B0d4a8Eb9db214"),
    "PinkLock": Web3.to_checksum_address("0x71B5759d73262FBb223956913ecF4ecC51057641"),
}


ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
]


def lp_analysis(w3, lp_pair_address):
    """
    On-chain LP verification (fallback only).
    DexScreener LP data should take priority.
    """

    try:
        lp = w3.eth.contract(
            address=Web3.to_checksum_address(lp_pair_address),
            abi=ERC20_ABI,
        )

        total_supply = lp.functions.totalSupply().call()
        if total_supply == 0:
            return {"status": "unknown"}

        # 🔥 Burn detection
        burned = 0
        for addr in BURN_ADDRESSES:
            try:
                burned += lp.functions.balanceOf(addr).call()
            except Exception:
                pass

        burned_pct = (burned / total_supply) * 100

        if burned_pct >= 90:
            return {
                "status": "burned",
                "burned_pct": round(burned_pct, 2),
                "source": "onchain",
            }

        # 🔒 Known locker detection
        for name, locker in KNOWN_LOCKERS.items():
            try:
                bal = lp.functions.balanceOf(locker).call()
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
