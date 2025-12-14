def scan_limits(bytecode):
    flags = []
    for keyword in ["blacklist", "pause", "setMax", "cooldown"]:
        if keyword.encode().hex() in bytecode:
            flags.append(keyword)
    return flags
