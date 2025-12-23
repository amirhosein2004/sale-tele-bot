# مدیریت وضعیت کاربران و instance های مشترک
from ...repository import DataManagerAdapter

# ایجاد یک instance مشترک از DataManagerAdapter (بجای DataManager قدیمی)
data_manager = DataManagerAdapter()

# داده‌های تستی - این بخش بعداً حذف خواهد شد
# import random
# for i in range(1, 300):
#    name = f"Product {i}"
#    quantity = random.randint(1, 50)
#    data_manager.add_product(name, quantity)

# ذخیره وضعیت کاربران
user_states = {}
user_data = {}
user_locks = {}  # قفل برای جلوگیری از کلیک‌های چندگانه
processing_users = set()  # کاربرانی که در حال پردازش هستند


def get_user_state(user_id):
    """دریافت وضعیت کاربر"""
    return user_states.get(user_id, "main_menu")


def set_user_state(user_id, state):
    """تعیین وضعیت کاربر"""
    user_states[user_id] = state


def get_user_data(user_id):
    """دریافت داده‌های موقت کاربر"""
    if user_id not in user_data:
        user_data[user_id] = {}
    return user_data[user_id]


def clear_user_data(user_id):
    """پاک کردن داده‌های موقت کاربر"""
    if user_id in user_data:
        user_data[user_id] = {}


def is_user_processing(user_id):
    """بررسی اینکه آیا کاربر در حال پردازش است"""
    return user_id in processing_users


def set_user_processing(user_id, processing=True):
    """تعیین وضعیت پردازش کاربر"""
    if processing:
        processing_users.add(user_id)
    else:
        processing_users.discard(user_id)
