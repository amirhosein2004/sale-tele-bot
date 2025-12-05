# تنظیمات اتصال دیتابیس
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os


DB_USER = os.environ["POSTGRES_USER"]
DB_PASS = os.environ["POSTGRES_PASSWORD"]
DB_HOST = os.environ.get("POSTGRES_HOST", "localhost")
DB_PORT = os.environ.get("POSTGRES_PORT", "5432")
DB_NAME = os.environ["POSTGRES_DB"]

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ساخت Engine: مسئول اتصال به دیتابیس و مدیریت اتصال‌ها
engine = create_engine(DATABASE_URL, echo=False, future=True)

# کارخانه ساخت Session: هر بار یک اتصال تراکنشی جدید به دیتابیس
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# پایه مدل‌ها: همه کلاس‌های مدل از این Base ارث می‌برند
Base = declarative_base()
