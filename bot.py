import asyncio
import time

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

from web3 import Web3

from config import BOT_TOKEN
from scanner.chain import detect_chain
from scanner.token import get_token_info
from scanner.trading import trading_enabled
from scanner.dexscreener import fetch_dex_data
from scanner.liquidity import lp_analysis

from scanner.goplus import fetch_goplus
from scanner.verdict import verdict_engine
from formatter import format_report


START_TEXT = "Paste any EVM token contract address to get an instant on-chain scan."


# ───────── Commands ─────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text(START_TEXT)
    await asyncio.sleep(10)
    try:
        await msg.delete()
    except Exception:
        pass


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text(START_TEXT)
    await asyncio.sleep(10)
    try:
        await msg.delete()
    except Exception:
        pass


# ───────── Scanner ─────────

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    ca = msg.text.strip()

    if not Web3.is_address(ca):
        return

    await context.bot.send_chat_action(
        chat_id=msg.chat.id,
        action=ChatAction.TYPING
    )

    status_msg = await msg.reply_text(
        "🔍 Scanning contract...",
        reply_to_message_id=msg.message_id
    )

    chain, w3 = detect_chain(ca)
    if not chain:
        await status_msg.edit_text("❌ Contract not found on supported chains")
        return

    ca = Web3.to_checksum_address(ca)

    # ───────── Core data ─────────
    token = get_token_info(w3, ca)
    market = fetch_dex_data(ca)
    trading = trading_enabled(True, market)
    goplus = fetch_goplus(chain, ca)

    # ───────── LP INFO (PRIORITY ORDER) ─────────
    # 1️⃣ DexScreener (authoritative)
    # 2️⃣ On-chain burn % fallback
    # 3️⃣ Known lockers (UNCX / TeamFinance)

    lp_info = {"status": "unknown"}

    if market and market.get("lp"):
        ds_lp = market["lp"]
        if ds_lp.get("status") == "burned":
            lp_info = {
                "status": "burned",
                "burned_pct": ds_lp.get("burnedPct"),
                "source": "dexscreener",
            }
        elif ds_lp.get("status") == "locked":
            lp_info = {
                "status": "locked",
                "locker": ds_lp.get("locker", "DexScreener"),
                "unlock_ts": ds_lp.get("unlockTs"),
            }

    # 2️⃣ On-chain LP verification (only if still unknown)
    if lp_info["status"] == "unknown" and market:
        try:
            pair_addr = market.get("pair_address")
            if pair_addr:
                lp_info = lp_analysis(w3, pair_addr)
        except Exception:
            pass

    # ───────── Data for verdict / formatter ─────────
    data = {
        "name": token.get("name", "Unknown"),
        "symbol": token.get("symbol", "UNKNOWN"),
        "owner_renounced": token.get("owner_renounced"),
        "owner_address": token.get("owner"),
        "trading": trading,
        "goplus": goplus,
        "pair_created": market.get("pair_created") if market else None,
    }

    verdict = verdict_engine(data, lp_info)

    text = format_report(
        data,
        verdict,
        market,
        lp_info,
        history=None
    )

    # ───────── Buttons ─────────
    buttons = []
    if market:
        row = []
        if market.get("dext"):
            row.append(InlineKeyboardButton("📊 DEXT", url=market["dext"]))
        if market.get("dexs"):
            row.append(InlineKeyboardButton("📈 DEXS", url=market["dexs"]))
        if row:
            buttons.append(row)

    sent = await status_msg.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons) if buttons else None,
        disable_web_page_preview=True
    )

    # 📌 Pin latest scan
    try:
        await context.bot.pin_chat_message(
            chat_id=sent.chat.id,
            message_id=sent.message_id,
            disable_notification=True
        )
    except Exception:
        pass


# ───────── App ─────────

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, scan))

    app.run_polling()


if __name__ == "__main__":
    main()
