import os
import json
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
)

# ======================
# 🔑 تنظیمات اصلی
# ======================

TOKEN = os.getenv("BOT_TOKEN")  # توکن از متغیر محیطی Railway خونده میشه
CONFIG_FILE = "config.json"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def load_config():
    # پیکربندی لینک‌ها
    data = {
        "socials": {
            "instagram": [
                {"name": "Instagram @Kaydarap", "url": "https://instagram.com/Kaydarap"}
            ],
            "tiktok": [
                {"name": "TikTok @Kaydarap", "url": "https://www.tiktok.com/@Kaydarap"}
            ],
            "telegram": [
                {"name": "Telegram @Kaydarap", "url": "https://t.me/Kaydarap"}
            ],
            "discord": [
                {"name": "Discord", "url": "https://discord.gg/YOUR_INVITE_CODE"}
            ],
            "whatsapp": [
                {"name": "WhatsApp", "url": "https://wa.me/16025662108"}
            ],
            "email": [
                {"name": "Email", "url": "mailto:Kaydarap@gmail.com"}
            ],
        }
    }
    return data


# ======================
# 🧩 ساخت منوها
# ======================

def build_main_menu():
    buttons = [
        [
            InlineKeyboardButton("📸 اینستاگرام", callback_data="social_instagram"),
            InlineKeyboardButton("🎵 تیک‌تاک", callback_data="social_tiktok"),
        ],
        [
            InlineKeyboardButton("💬 تلگرام", callback_data="social_telegram"),
            InlineKeyboardButton("🎮 دیسکورد", callback_data="social_discord"),
        ],
        [
            InlineKeyboardButton("📱 واتساپ", callback_data="social_whatsapp"),
            InlineKeyboardButton("✉️ ایمیل", callback_data="social_email"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def build_links_keyboard(items):
    buttons = [[InlineKeyboardButton(it["name"], url=it["url"])] for it in items]
    buttons.append([InlineKeyboardButton("🔙 برگشت به منو", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(buttons)


# ======================
# 🧠 فرمان‌ها
# ======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "سلام 👋\n"
        "به ربات Kaydarap خوش اومدی!\n"
        "یکی از شبکه‌های اجتماعی زیر رو انتخاب کن 👇"
    )
    await update.message.reply_text(text, reply_markup=build_main_menu())


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_to_menu":
        await query.edit_message_text(
            "یکی از شبکه‌های اجتماعی زیر رو انتخاب کن 👇",
            reply_markup=build_main_menu(),
        )
        return

    if data.startswith("social_"):
        key = data.split("social_")[1]
        cfg = load_config()
        socials = cfg.get("socials", {})
        items = socials.get(key)

        if items:
            title_map = {
                "instagram": "اینستاگرام",
                "tiktok": "تیک‌تاک",
                "telegram": "تلگرام",
                "discord": "دیسکورد",
                "whatsapp": "واتساپ",
                "email": "ایمیل",
            }
            title = title_map.get(key, key.capitalize())
            await query.edit_message_text(
                f"📱 اکانت‌های {title}:",
                reply_markup=build_links_keyboard(items),
            )
        else:
            await query.edit_message_text(
                "برای این شبکه هنوز اکانتی ثبت نشده.",
                reply_markup=build_main_menu(),
            )


# ======================
# 🚀 اجرای ربات
# ======================

def main():
    if not TOKEN:
        raise RuntimeError("⚠️ متغیر محیطی BOT_TOKEN تنظیم نشده است!")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))

    print("✅ ربات Kaydarap در حال اجراست ...")
    app.run_polling()


if __name__ == "__main__":
    main()
