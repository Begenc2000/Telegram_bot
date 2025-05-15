import logging
import ccxt
import pandas as pd
import pandas_ta as ta
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Telegram Bot Token
TOKEN = "7381017456:AAGfHPIbC67w3yZRik65AFObrNive24UWJ0"  # Buraya kendi bot token'ınızı yazın

# Başlangıç ayarları
timeframe = '4h'
squeeze_threshold = 1.0  # yüzde

# Telegram log
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Binance verisi için
exchange = ccxt.binance({
    'enableRateLimit': True
})


def get_symbols():
    markets = exchange.load_markets()
    return [symbol for symbol in markets if symbol.endswith('/USDT') and not symbol.startswith('1000')]


def fetch_ohlcv(symbol, tf):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, tf, limit=100)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        return df
    except Exception:
        return None


def is_bollinger_squeeze(df, threshold):
    bb = ta.bbands(df['close'], length=20, std=2)
    if bb is None or bb['BBU_20_2.0'].isna().all():
        return False
    df = df.join(bb)
    df.dropna(inplace=True)
    if df.empty:
        return False
    latest = df.iloc[-1]
    width = (latest['BBU_20_2.0'] - latest['BBL_20_2.0']) / latest['BBM_20_2.0'] * 100
    return width < threshold


def scan(update: Update, context: CallbackContext):
    update.message.reply_text(f"Taranıyor... Zaman dilimi: {timeframe}, Sıkışma eşiği: %{squeeze_threshold}")
    coins = get_symbols()
    matched = []

    for coin in coins:
        df = fetch_ohlcv(coin, timeframe)
        if df is not None and is_bollinger_squeeze(df, squeeze_threshold):
            matched.append(coin)

    if matched:
        text = "Sıkışma tespit edilen coinler:\n" + "\n".join(matched)
    else:
        text = "Sıkışma bulunan coin yok."
    update.message.reply_text(text)


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


def start(update: Update, context: CallbackContext):
    update.message.reply_text("Bollinger Sıkışma Botu başlatıldı!\nKomutlar:\n/scan\n/set_timeframe [4h|1d]\n/set_threshold [yüzde]")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("scan", scan))
    dp.add_handler(CommandHandler("set_timeframe", set_timeframe))
    dp.add_handler(CommandHandler("set_threshold", set_threshold))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
