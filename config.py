import os
from dotenv import load_dotenv

# Load .env locally (Heroku ignores this safely)
load_dotenv()

# ───────── Telegram ─────────
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not set")

# ───────── Infura ─────────
INFURA_KEY = os.getenv("INFURA_KEY")
if not INFURA_KEY:
    raise RuntimeError("INFURA_KEY not set")

# ───────── RPCs ─────────
RPCS = {
    "ETH": f"https://mainnet.infura.io/v3/{INFURA_KEY}",
    "BSC": f"https://bsc-mainnet.infura.io/v3/{INFURA_KEY}",
    "BASE": f"https://base-mainnet.infura.io/v3/{INFURA_KEY}",
    "MONAD": f"https://monad-mainnet.infura.io/v3/{INFURA_KEY}",
}

# ───────── DEX Routers ─────────
DEX_ROUTERS = {
    "ETH": {
        "router": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
        "weth": "0xC02aaA39b223FE8D0A0E5C4F27eAD9083C756Cc2",
    },
    "BSC": {
        "router": "0x10ED43C718714eb63d5aA57B78B54704E256024E",
        "weth": "0xBB4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
    },
    "BASE": {
        "router": "0x327Df1E6de05895d2ab08513aaDD9313Fe505d86",
        "weth": "0x4200000000000000000000000000000000000006",
    },
}

# ───────── Optional Settings ─────────
CALLER_ALERT_THRESHOLD = int(
    os.getenv("CALLER_ALERT_THRESHOLD", "5")
)
