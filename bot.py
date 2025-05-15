import logging
import ccxt
import pandas as pd
import pandas_ta as ta
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from apscheduler.schedulers.background import BackgroundScheduler
import threading

TOKEN = "7915865978:AAEcIjjwfzLJu-5RMNGW8BV0SzDIuee6GyA"

# Ayarlar
timeframe = '4h'
squeeze_threshold = 1.0  # yüzde
squeeze_bars = 3  # sıkışma kontrolü için bar sayısı
auto_scan = False
auto_scan_interval = 30  # dakika

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

exchange = ccxt.binance({
    'enableRateLimit': True
})

ALLOWED_USERS = []

scheduler = BackgroundScheduler()
scheduler.start()
auto_scan_chat_id = None


def get_symbols():
    try:
        markets = exchange.load_markets()
        return [symbol for symbol in markets if symbol.endswith('/USDT') and not symbol.startswith('1000') and not symbol.startswith('USD')]
    except Exception as e:
        logger.error(f"Market verileri yüklenemedi: {e}")
        return []


def fetch_ohlcv(symbol, tf):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, tf, limit=100)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        return df
    except Exception as e:
        logger.error(f"{symbol} için OHLCV verisi alınamadı: {e}")
        return None


def is_bollinger_squeeze(df, threshold, bars):
    bb = ta.bbands(df['close'], length=20, std=2)
    if bb is None or bb.isna().all().any():
        return False
    df = df.join(bb).dropna()
    if len(df) < bars:
        return False
    df['width'] = (df['BBU_20_2.0'] - df['BBL_20_2.0']) / df['BBM_20_2.0'] * 100
    return (df['width'].iloc[-bars:] < threshold).all()


def perform_scan(context: CallbackContext, chat_id):
    coins = get_symbols()
    matched = []
    for idx, coin in enumerate(coins):
        df = fetch_ohlcv(coin, timeframe)
        if df is not None and is_bollinger_squeeze(df, squeeze_threshold, squeeze_bars):
            matched.append(coin)
        if idx % 50 == 0:
            context.bot.send_message(chat_id=chat_id, text=f"{idx}/{len(coins)} coin tarandı...")

    if matched:
        text = "\u2705 Sıkışma tespit edilen coinler:\n" + "\n".join(matched)
    else:
        text = "\u274C Sıkışma bulunan coin yok."
    context.bot.send_message(chat_id=chat_id, text=text)


def scan(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    update.message.reply_text(f"Taranıyor... Zaman dilimi: {timeframe}, Eşik: %{squeeze_threshold}, Bar sayısı: {squeeze_bars}")
    threading.Thread(target=perform_scan, args=(context, chat_id)).start()


def set_timeframe(update: Update, context: CallbackContext):
    global timeframe
    if context.args and context.args[0] in ['4h', '1d']:
        timeframe = context.args[0]
        update.message.reply_text(f"Zaman dilimi {timeframe} olarak ayarlandı.")
    else:
        update.message.reply_text("Kullanım: /set_timeframe 4h veya 1d")


def set_threshold(update: Update, context: CallbackContext):
    global squeeze_threshold
    try:
        value = float(context.args[0])
        squeeze_threshold = value
        update.message.reply_text(f"Sıkışma eşiği %{value} olarak ayarlandı.")
    except:
        update.message.reply_text("Kullanım: /set_threshold 1.5")


def set_bars(update: Update, context: CallbackContext):
    global squeeze_bars
    try:
        value = int(context.args[0])
        squeeze_bars = value
        update.message.reply_text(f"Kontrol edilecek bar sayısı {value} olarak ayarlandı.")
    except:
        update.message.reply_text("Kullanım: /set_bars 3")


def set_interval(update: Update, context: CallbackContext):
    global auto_scan_interval
    try:
        value = int(context.args[0])
        auto_scan_interval = value
        update.message.reply_text(f"Otomatik tarama aralığı {value} dakika olarak ayarlandı.")
    except:
        update.message.reply_text("Kullanım: /set_interval 30")


def start_auto(update: Update, context: CallbackContext):
    global auto_scan, auto_scan_chat_id
    auto_scan = True
    auto_scan_chat_id = update.effective_chat.id
    scheduler.add_job(perform_scan, 'interval', minutes=auto_scan_interval, args=[context, auto_scan_chat_id], id='auto_scan', replace_existing=True)
    update.message.reply_text(f"Otomatik tarama başlatıldı. Her {auto_scan_interval} dakikada bir çalışacak.")


def stop_auto(update: Update, context: CallbackContext):
    global auto_scan
    auto_scan = False
    scheduler.remove_job('auto_scan')
    update.message.reply_text("Otomatik tarama durduruldu.")


def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Taramayı Başlat", callback_data='scan')],
        [InlineKeyboardButton("Zaman Dilimi", callback_data='set_tf')],
        [InlineKeyboardButton("Sıkışma Eşiği", callback_data='set_thresh')],
        [InlineKeyboardButton("Bar Sayısı", callback_data='set_bars')],
        [InlineKeyboardButton("Oto Başlat", callback_data='start_auto')],
        [InlineKeyboardButton("Oto Durdur", callback_data='stop_auto')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("\U0001F4C8 Bollinger Sıkışma Botu\nKomut seçin:", reply_markup=reply_markup)


def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if query.data == 'scan':
        scan(query, context)
    elif query.data == 'set_tf':
        query.edit_message_text("Zaman dilimini şu komutla ayarlayın: /set_timeframe 4h veya 1d")
    elif query.data == 'set_thresh':
        query.edit_message_text("Eşiği şu komutla ayarlayın: /set_threshold 1.5")
    elif query.data == 'set_bars':
        query.edit_message_text("Bar sayısını şu komutla ayarlayın: /set_bars 3")
    elif query.data == 'start_auto':
        start_auto(query, context)
    elif query.data == 'stop_auto':
        stop_auto(query, context)


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("scan", scan))
    dp.add_handler(CommandHandler("set_timeframe", set_timeframe))
    dp.add_handler(CommandHandler("set_threshold", set_threshold))
    dp.add_handler(CommandHandler("set_bars", set_bars))
    dp.add_handler(CommandHandler("set_interval", set_interval))
    dp.add_handler(CommandHandler("start_auto", start_auto))
    dp.add_handler(CommandHandler("stop_auto", stop_auto))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
