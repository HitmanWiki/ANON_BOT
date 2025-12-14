from web3 import Web3
from config import RPCS

def detect_chain(ca):
    for chain, rpc in RPCS.items():
        try:
            w3 = Web3(Web3.HTTPProvider(rpc))
            if w3.is_connected():
                code = w3.eth.get_code(Web3.to_checksum_address(ca))
                if code and len(code) > 2:
                    return chain, w3
        except:
            continue
    return None, None
