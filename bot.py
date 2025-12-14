from telegram.ext import Application, MessageHandler, filters
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from web3 import Web3

from config import BOT_TOKEN
from scanner.chain import detect_chain
from scanner.token import get_token_info
from scanner.trading import trading_enabled
from scanner.honeypot import simulate_trade
from scanner.honeypot_is import check_honeypot_is
from scanner.dexscreener import fetch_dex_data, volume_spike
from scanner.liquidity import lp_analysis
from scanner.goplus import fetch_goplus
from scanner.verdict import verdict_engine
from formatter import format_report
from scanner.abi.uniswap_pair import UNISWAP_PAIR_ABI
from telegram.constants import ChatAction



TOKEN_STATE = {}

async def scan(update: Update, context):
    msg = update.message
    ca = msg.text.strip()
    if not Web3.is_address(ca):
        return

    # Show typing indicator
    await context.bot.send_chat_action(
        chat_id=msg.chat.id,
        action=ChatAction.TYPING
    )

    await msg.reply_text(
        "🔍 Scanning contract...",
        reply_to_message_id=msg.message_id
    )


    chain, w3 = detect_chain(ca)
    if not chain:
        await msg.reply_text("❌ Contract not found", reply_to_message_id=msg.message_id)
        return

    ca = Web3.to_checksum_address(ca)
    bytecode = w3.eth.get_code(ca).hex()

    token = get_token_info(w3, ca)
    market = fetch_dex_data(ca)
    trading = trading_enabled(True, market)

    trade_sim = simulate_trade(w3, chain, ca)
    hp_is = check_honeypot_is(chain, ca)

    # 🛡 GoPlus
    goplus = fetch_goplus(chain, ca)

    

    # ALWAYS initialize first
    lp_info = {"status": "unknown"}

    if market:
        pair_address = market.get("pair_address")

        if pair_address:
            from scanner.abi.uniswap_pair import UNISWAP_PAIR_ABI

            try:
                pair = w3.eth.contract(
                    address=Web3.to_checksum_address(pair_address),
                    abi=UNISWAP_PAIR_ABI
                )
                total_supply = pair.functions.totalSupply().call()
                lp_info = lp_analysis(w3, pair, total_supply)
            except Exception:
                lp_info = {"status": "unknown"}



    data = {
        "name": token["name"],
        "symbol": token["symbol"],
        "owner": token["owner"],
        "trading": trading,
        "sell_test": trade_sim.get("sell_test"),
        "honeypot_is": hp_is,
        "goplus": goplus,
        "advanced_flags": [],
    }

    verdict = verdict_engine(data)

    prev = TOKEN_STATE.get(ca)
    history = {"prev_score": prev["score"]} if prev else None
    TOKEN_STATE[ca] = {"score": verdict["score"]}

    text = format_report(data, verdict, market, lp_info, history)

    buttons = []
    if market:
        row = []
        if market.get("dext"):
            row.append(InlineKeyboardButton("📊 DEXT", url=market["dext"]))
        if market.get("dexs"):
            row.append(InlineKeyboardButton("📈 DEXS", url=market["dexs"]))
        if row:
            buttons.append(row)

    sent = await msg.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons) if buttons else None,
        reply_to_message_id=msg.message_id
    )

    # 📌 Pin the latest scan message
    try:
        await context.bot.pin_chat_message(
            chat_id=sent.chat.id,
            message_id=sent.message_id,
            disable_notification=True
        )
    except Exception:
        pass  # ignore if bot lacks pin permission


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, scan))
    app.run_polling()

if __name__ == "__main__":
    main()
