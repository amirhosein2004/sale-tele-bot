# فایل اصلی ربات
import telebot
from .config import BOT_TOKEN
from .handlers import register_handlers  

# ایجاد نمونه ربات
bot = telebot.TeleBot(BOT_TOKEN)

# ثبت تمام هندلرها
register_handlers(bot)

if __name__ == "__main__":
    print("🤖 bot is runnig ...")
    print("for terminate click Ctrl+C")
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("\n🛑bot stoped.")
