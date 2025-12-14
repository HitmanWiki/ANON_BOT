def deployer_reputation(w3, deployer):
    tx_count = w3.eth.get_transaction_count(deployer)
    balance = w3.eth.get_balance(deployer)

    flags = []

    if tx_count < 5:
        flags.append("Fresh deployer wallet")

    if balance == 0:
        flags.append("No remaining ETH balance")

    return flags
