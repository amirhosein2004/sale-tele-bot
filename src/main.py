# فایل اصلی ربات

import telebot
from . import config
from .handlers import register_handlers  


# اگر پراکسی وجود داشت
if config.PROXY:
    proxy_url = config.PROXY["url"]

    # اگر پراکسی user/pass میخواست و داشت
    if config.PROXY.get("username") and config.PROXY.get("password"):
        telebot.apihelper.proxy = {
            "http":  f"socks5://{config.PROXY['username']}:{config.PROXY['password']}@{proxy_url}",
            "https": f"socks5://{config.PROXY['username']}:{config.PROXY['password']}@{proxy_url}",
        }
    else:
        # پراکسی بدون user/pass
        telebot.apihelper.proxy = {
            "http":  f"socks5://{proxy_url}",
            "https": f"socks5://{proxy_url}",
        }

# ایجاد نمونه ربات
bot = telebot.TeleBot(config.BOT_TOKEN)

# ثبت تمام هندلرها
register_handlers(bot)

if __name__ == "__main__":
    print("🤖 bot is runnig ...")
    print("for terminate click Ctrl+C")
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("\n🛑bot stoped.")
