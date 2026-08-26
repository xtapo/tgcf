import asyncio
import io
import os
import sys

# Đảm bảo UTF-8 cho console Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from telethon import TelegramClient
from telethon.sessions import StringSession
from tgcf.config import CONFIG

async def main():
    print("========================================")
    print("      KIEM TRA KET NOI TELEGRAM")
    print("========================================")
    api_id = CONFIG.login.API_ID or int(os.getenv("API_ID", 0))
    api_hash = CONFIG.login.API_HASH or os.getenv("API_HASH", "")
    bot_token = CONFIG.login.BOT_TOKEN or os.getenv("BOT_TOKEN", "")
    session_string = CONFIG.login.SESSION_STRING or os.getenv("SESSION_STRING", "")
    user_type = CONFIG.login.user_type  # 0: Bot, 1: User

    print(f"- API_ID: {api_id}")
    print(f"- Loai tai khoan: {'Bot' if user_type == 0 else 'User'}")

    if not api_id or not api_hash:
        print("❌ Lỗi: Chưa có API_ID hoặc API_HASH trong file .env hoặc tgcf.config.yml!")
        return

    try:
        if user_type == 0:
            # Bot Account
            if not bot_token:
                print("❌ Lỗi: Bạn đang chọn loại tài khoản Bot nhưng chưa nhập BOT_TOKEN!")
                print("👉 Hãy vào trang 1_🔑_Telegram_Login trên Web UI hoặc thêm BOT_TOKEN=... vào file .env")
                return
            client = TelegramClient("tgcf_bot_check", api_id, api_hash)
            await client.start(bot_token=bot_token)
        else:
            # User Account
            if session_string:
                print("- Su dung SESSION_STRING co san...")
                session = StringSession(session_string)
                client = TelegramClient(session, api_id, api_hash)
                await client.connect()
                if not await client.is_user_authorized():
                    print("❌ SESSION_STRING khong hop le hoac da het han!")
                    return
            else:
                print("- Dang su dung file session ('tgcf_user')...")
                client = TelegramClient("tgcf_user", api_id, api_hash)
                await client.start()

        me = await client.get_me()
        if me:
            print("\n" + "="*50)
            print("🎉 KẾT NỐI TELEGRAM THÀNH CÔNG!")
            print(f"👉 Tên: {me.first_name} {me.last_name or ''}".strip())
            print(f"👉 Username: @{me.username}" if me.username else "👉 Username: (Không có)")
            print(f"👉 Telegram ID: {me.id}")
            print(f"👉 Loại: {'Bot' if me.bot else 'User Account'}")

            # Xuất chuỗi Session String cho User Account
            if not me.bot:
                session_str = StringSession.save(client.session)
                print("\n📋 CHUỖI SESSION STRING CỦA BẠN:")
                print("-" * 50)
                print(session_str)
                print("-" * 50)
                print("💡 Bạn có thể copy chuỗi trên dán vào ô 'Enter session string' trong Web UI!")

            print("="*50 + "\n")
        else:
            print("❌ Không thể lấy thông tin tài khoản Telegram.")

        await client.disconnect()
    except Exception as e:
        print(f"\n❌ LỖI KẾT NỐI: {e}")

if __name__ == "__main__":
    asyncio.run(main())



