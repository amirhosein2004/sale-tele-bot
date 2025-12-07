# فایل اصلی ربات

import telebot
from .core.config import settings
from .bot.handlers import register_handlers


# اگر پراکسی وجود داشت
if settings.PROXY:
    proxy_config = settings.PROXY
    proxy_url = proxy_config.url

    # اگر پراکسی user/pass میخواست و داشت
    if proxy_config.username and proxy_config.password:
        telebot.apihelper.proxy = {
            "http": f"socks5://{proxy_config.username}:{proxy_config.password}@{proxy_url}",
            "https": f"socks5://{proxy_config.username}:{proxy_config.password}@{proxy_url}",
        }
    else:
        # پراکسی بدون user/pass
        telebot.apihelper.proxy = {
            "http": f"socks5://{proxy_url}",
            "https": f"socks5://{proxy_url}",
        }

# ایجاد نمونه ربات
bot = telebot.TeleBot(settings.BOT_TOKEN)

# ثبت تمام هندلرها
register_handlers(bot)

if __name__ == "__main__":
    print("🤖 bot is runnig ...")
    print("for terminate click Ctrl+C")
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("\n🛑bot stoped.")
