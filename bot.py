import os

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Updater, CallbackContext, CommandHandler, ConversationHandler, CallbackQueryHandler)

from binance_p2p_api import get_exchange_rate


def start(update: Update, context: CallbackContext):
    text = """Привет!
Я бот, у меня есть предназначение. Я помогаю получить реальный курс, рассчитанный исходя из цены покупки и продажи криптовалют.
Сейчас я умею только получить текущий курс, но постепенно учусь новому.
    
Моя функциональность дорабатывается, если у тебя есть предложения, пиши в тг создателя @kosyanforyou
"""
    # context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    keyboard = [[InlineKeyboardButton("Получить курс валют", callback_data='Текущий курс')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text, reply_markup=reply_markup)
    return "Prompt"


def get_usd_and_eur_rate(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    usd = get_exchange_rate("RUB", "USD")
    eur = get_exchange_rate("RUB", "EUR")
    text = f"""Лучший текущий курс на binance p2p:
EUR --> {eur}
USD --> {usd}
Расчет производился через промежуточную валюту - ETH.
При расчете курса не учитывается количество покупаемой и продаваемой валюты. \
Расчет курса с указанным количеством валюты в разработке.
😘❤️🌚"""
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    return ConversationHandler.END


if __name__ == '__main__':
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    updater = Updater(token=token)
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            "Prompt": [
                CallbackQueryHandler(get_usd_and_eur_rate, pattern='^' + "Текущий курс" + '$')
            ]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
