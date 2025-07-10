from telethon import TelegramClient
import asyncio
import datetime

# ================== AYARLAR =================== #
api_id = 123456  # <-- my.telegram.org'dan aldığın api_id
api_hash = 'abcdef1234567890abcdef1234567890'  # <-- api_hash

SEND_EVERY_MINUTES = 15  # Kaç dakikada bir gönderi yapılacak
from_chat = 'kanaladiniz'   # Örn: '@mychannel'
message_id = 123            # Paylaşılacak mesajın ID'si

# Grupların listesi
GROUPS = [
    'grup_adi_1',
    'grup_adi_2',
    'grup_adi_3'
]
# ============================================== #

client = TelegramClient('my_session', api_id, api_hash)

async def send_to_groups():
    for group in GROUPS:
        try:
            await client.forward_messages(group, message_id, from_chat)
            print(f"✅ {datetime.datetime.now().strftime('%H:%M:%S')} | Gönderildi: {group}")
            await asyncio.sleep(2)  # Gruplar arası bekleme
        except Exception as e:
            print(f"❌ {datetime.datetime.now().strftime('%H:%M:%S')} | HATA ({group}): {e}")

async def main_loop():
    while True:
        print(f"\n🔄 Yeni döngü: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await send_to_groups()
        print(f"⏳ Bekleniyor: {SEND_EVERY_MINUTES} dakika...\n")
        await asyncio.sleep(SEND_EVERY_MINUTES * 60)

with client:
    client.loop.run_until_complete(main_loop())
