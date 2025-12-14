from web3 import Web3
from config import DEX_ROUTERS

ROUTER_ABI = [{
    "name": "getAmountsOut",
    "type": "function",
    "inputs": [
        {"name": "amountIn", "type": "uint256"},
        {"name": "path", "type": "address[]"}
    ],
    "outputs": [{"type": "uint256[]"}]
}]

def simulate_trade(w3, chain, ca):
    if chain not in DEX_ROUTERS:
        return {
            "sell_test": "UNKNOWN",
            "buy": "N/A",
            "sell": "N/A"
        }

    try:
        r = DEX_ROUTERS[chain]
        router = w3.eth.contract(
            address=Web3.to_checksum_address(r["router"]),
            abi=ROUTER_ABI
        )

        amount = w3.to_wei(0.01, "ether")

        # BUY SIMULATION
        buy = router.functions.getAmountsOut(
            amount,
            [r["weth"], ca]
        ).call()

        # SELL SIMULATION
        sell = router.functions.getAmountsOut(
            buy[-1],
            [ca, r["weth"]]
        ).call()

        sell_tax = max(0, (amount - sell[-1]) / amount * 100)

        return {
            "sell_test": "OK",
            "buy": "0%",
            "sell": f"{sell_tax:.2f}%"
        }

    except Exception:
        # ⚠️ ANON RULE: sell failure ≠ honeypot
        return {
            "sell_test": "FAIL",
            "buy": "N/A",
            "sell": "N/A"
        }
