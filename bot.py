import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import ccxt
import talib

# Bot Token
TOKEN = '7915865978:AAEcIjjwfzLJu-5RMNGW8BV0SzDIuee6GyA'

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Borsaya Bağlantı (BingX API)
exchange = ccxt.bingx({
    'apiKey': '4qLGzeAiRO7vLjQmWk21lfFJpeP8wh7IIS60ERf0zAdSemRCYAhWjGDH6MfmCpU5WZ5t0mqIShG2cO4oJqQ',
    'secret': '5yrz8BdFeppsi665Xkcu19CVfD7DOssphaZ0IGstg2TZfOCuQYQIEjBhsn3kFGrpX2cPhBMcSAU20yFhzSvA',
})

# Kullanıcıya sunulacak seçenekler
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Merhaba! Trading botumuza hoş geldiniz.\n\n"
        "Analiz yapmak için aşağıdaki seçeneklerden birini seçebilirsiniz:\n\n"
        "/set_timedelta - Zaman dilimini seçin\n"
        "/set_rsi - RSI eşik değerini belirleyin\n"
        "/set_macd - MACD parametrelerini belirleyin\n"
        "/set_volatility - Volatilite kriterlerini ayarlayın\n"
    )

# Zaman Dilimi Seçimi
def set_timedelta(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Zaman dilimini seçin:\n"
        "1. 15 Dakika\n"
        "2. 1 Saat\n"
        "3. 4 Saat\n"
        "4. 1 Gün"
    )

# RSI Seçimi
def set_rsi(update: Update, context: CallbackContext):
    update.message.reply_text(
        "RSI eşiğini seçin:\n"
        "1. Aşırı Satım (30 altı)\n"
        "2. Aşırı Alım (70 üstü)"
    )

# MACD Seçimi
def set_macd(update: Update, context: CallbackContext):
    update.message.reply_text(
        "MACD parametrelerini seçin:\n"
        "1. Kısa vadeli MACD'nin uzun vadeli MACD'yi yukarıya kesmesi (alım sinyali)\n"
    )

# Volatilite Seçimi
def set_volatility(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Volatilite kriterlerini ayarlayın:\n"
        "1. Bollinger Bands\n"
        "2. Fiyat Dalgalanması"
    )

# Verileri Analiz Etme (Kısa Örnek)
def analyze(update: Update, context: CallbackContext):
    symbol = "BTC/USDT"
    timeframe = '1h'  # Örneğin 1 saatlik zaman dilimi

    # Binance'den veri çekme
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
    close_prices = [x[4] for x in ohlcv]

    # RSI hesaplama
    rsi = talib.RSI(close_prices, timeperiod=14)
    last_rsi = rsi[-1]

    # Eğer RSI 30'un altında ise, alım sinyali
    if last_rsi < 30:
        update.message.reply_text(f"RSI: {last_rsi} - Aşırı Satım! Potansiyel alım sinyali.")
    else:
        update.message.reply_text(f"RSI: {last_rsi} - Durum: Normal")

# Main
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("set_timedelta", set_timedelta))
    dp.add_handler(CommandHandler("set_rsi", set_rsi))
    dp.add_handler(CommandHandler("set_macd", set_macd))
    dp.add_handler(CommandHandler("set_volatility", set_volatility))
    dp.add_handler(CommandHandler("analyze", analyze))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
