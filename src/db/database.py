# تنظیمات اتصال دیتابیس
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from ..core.config import settings

# آدرس دیتابیس
DATABASE_URL = settings.DATABASE_URL

# ساخت Engine: مسئول اتصال به دیتابیس و مدیریت اتصال‌ها
engine = create_engine(DATABASE_URL, echo=False, future=True)

# کارخانه ساخت Session: هر بار یک اتصال تراکنشی جدید به دیتابیس
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# پایه مدل‌ها: همه کلاس‌های مدل از این Base ارث می‌برند
Base = declarative_base()
