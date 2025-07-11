
from telethon import TelegramClient
import asyncio
import datetime
import random
import os
from threading import Thread
from flask import Flask

# Keep alive web server
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot çalışıyor! 🤖"

def run_flask():
    app.run(host='0.0.0.0', port=5000)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ================== AYARLAR =================== #
# Environment variables'dan alınacak (Replit Secrets kullanın)
# HESAP 1
api_id_1 = int(os.getenv('API_ID', '0'))
api_hash_1 = os.getenv('API_HASH', 'your_api_hash_here')

# HESAP 2
api_id_2 = int(os.getenv('API_ID_2', '0'))
api_hash_2 = os.getenv('API_HASH_2', 'your_api_hash_2_here')

SEND_EVERY_MINUTES = 120  # Kaç dakikada bir gönderi yapılacak
DELAY_BETWEEN_ACCOUNTS = 12  # Hesaplar arası bekleme (10-15 dakika)
from_chat = '@begacloudmining'
message_id = 3014

# HESAP 1 GRUPLARI
GROUPS_ACCOUNT_1 = [
    'https://t.me/ShareTrxCryptoLegit',
    'https://t.me/ShareMoneyCrypto', 
    'https://t.me/ShareTRXDOGEUSDTBNBCryptoLegit',
    'https://t.me/ShareTrons',
    'https://t.me/Earning_Group',
    'https://t.me/shareusdtlink2ceo',
    'https://t.me/trcoinkazanma'
]

# HESAP 2 GRUPLARI
GROUPS_ACCOUNT_2 = [
    'https://t.me/usdtsharelink1ceo',
    'https://t.me/tgrefim',
    'https://t.me/AirdropPaylasimTurkiye',
    'https://t.me/earningtrxsharelink338',
    'https://t.me/ShareMoneyCrypto',
    'https://t.me/trcoinkazanma',
    'https://t.me/BBC6772',
    'https://t.me/xglobalventures',
    'https://t.me/ShareTrons'
]
# ============================================== #

client_1 = TelegramClient('account_1_session', api_id_1, api_hash_1)
client_2 = TelegramClient('account_2_session', api_id_2, api_hash_2)

async def send_to_groups_account_1():
    print("📱 HESAP 1 paylaşıma başlıyor...")
    for group in GROUPS_ACCOUNT_1:
        try:
            await client_1.forward_messages(group, message_id, from_chat)
            print(f"✅ {datetime.datetime.now().strftime('%H:%M:%S')} | HESAP 1 | Gönderildi: {group}")
            random_wait = random.randint(3, 7)
            await asyncio.sleep(random_wait)
        except Exception as e:
            print(f"❌ {datetime.datetime.now().strftime('%H:%M:%S')} | HESAP 1 HATA ({group}): {e}")

async def send_to_groups_account_2():
    print("📱 HESAP 2 paylaşıma başlıyor...")
    for group in GROUPS_ACCOUNT_2:
        try:
            await client_2.forward_messages(group, message_id, from_chat)
            print(f"✅ {datetime.datetime.now().strftime('%H:%M:%S')} | HESAP 2 | Gönderildi: {group}")
            random_wait = random.randint(3, 7)
            await asyncio.sleep(random_wait)
        except Exception as e:
            print(f"❌ {datetime.datetime.now().strftime('%H:%M:%S')} | HESAP 2 HATA ({group}): {e}")

async def main_loop():
    while True:
        print(f"\n🔄 Yeni döngü: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # HESAP 1 paylaşım yap
        await send_to_groups_account_1()
        
        # 10-15 dakika bekle
        delay_minutes = random.randint(DELAY_BETWEEN_ACCOUNTS, DELAY_BETWEEN_ACCOUNTS + 3)
        print(f"⏳ Hesaplar arası bekleme: {delay_minutes} dakika...")
        await asyncio.sleep(delay_minutes * 60)
        
        # HESAP 2 paylaşım yap
        await send_to_groups_account_2()
        
        # Ana bekleme (120 dakika)
        random_minutes = random.randint(SEND_EVERY_MINUTES, SEND_EVERY_MINUTES + 10)
        print(f"⏳ Ana bekleme: {random_minutes} dakika...\n")
        await asyncio.sleep(random_minutes * 60)

async def run_bot():
    # API bilgileri kontrolü
    if api_id_1 == 0 or api_hash_1 == 'your_api_hash_here':
        print("❌ HATA: API_ID ve API_HASH environment variables'ları ayarlanmamış!")
        print("Replit Secrets kullanarak şu değerleri ekleyin:")
        print("- API_ID")
        print("- API_HASH") 
        print("- API_ID_2")
        print("- API_HASH_2")
        return
    
    await client_1.start()
    await client_2.start()
    print("🤖 İki hesap da başlatıldı!")
    await main_loop()

if __name__ == "__main__":
    keep_alive()  # Web server başlat
    asyncio.run(run_bot())
