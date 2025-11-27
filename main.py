import os
import logging
from typing import Set

from openai import OpenAI
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

# ======================
# 🔑 Settings
# ======================

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is not set.")

# OpenAI client (AI support)
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Users who are currently in AI support mode
AI_USERS: Set[int] = set()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ======================
# 📎 Social links (only Instagram & Telegram)
# ======================

INSTAGRAM_URL = "https://instagram.com/Kaydarap"
TELEGRAM_URL = "https://t.me/Kaydarap"


# ======================
# 🧩 Keyboards
# ======================

def build_main_menu() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton("📸 Instagram", callback_data="social_instagram"),
            InlineKeyboardButton("💬 Telegram", callback_data="social_telegram"),
        ],
        [
            InlineKeyboardButton("🤖 AI Support", callback_data="support_ai"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


# ======================
# 🧠 Commands
# ======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show main menu"""
    user_id = update.effective_user.id
    AI_USERS.discard(user_id)  # leave AI mode if user was in it

    text = (
        "Hey! 👋\n"
        "Welcome to the Kaydarap bot.\n"
        "Choose one of the options below 👇"
    )

    if update.message:
        await update.message.reply_text(text, reply_markup=build_main_menu())
    else:
        # If called from a callback
        await update.callback_query.edit_message_text(
            text, reply_markup=build_main_menu()
        )


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return to main menu with /menu"""
    user_id = update.effective_user.id
    AI_USERS.discard(user_id)

    text = "Back to main menu 👇"
    await update.message.reply_text(text, reply_markup=build_main_menu())


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline buttons"""
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data == "back_to_menu":
        AI_USERS.discard(user_id)
        await query.edit_message_text(
            "Choose one of the options below 👇",
            reply_markup=build_main_menu(),
        )
        return

    if data == "support_ai":
        # Enter AI support mode
        if not openai_client:
            await query.edit_message_text(
                "AI support is not configured yet. Please try again later.",
                reply_markup=build_main_menu(),
            )
            return

        AI_USERS.add(user_id)
        await query.edit_message_text(
            "🤖 You are now in AI Support mode.\n"
            "Ask me anything.\n"
            "To go back to the menu, type /menu.",
        )
        return

    if data == "social_instagram":
        await query.edit_message_text(
            "📸 Instagram profile:",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Instagram @Kaydarap", url=INSTAGRAM_URL)],
                    [InlineKeyboardButton("⬅️ Back to menu", callback_data="back_to_menu")],
                ]
            ),
        )
        return

    if data == "social_telegram":
        await query.edit_message_text(
            "💬 Telegram profile:",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Telegram @Kaydarap", url=TELEGRAM_URL)],
                    [InlineKeyboardButton("⬅️ Back to menu", callback_data="back_to_menu")],
                ]
            ),
        )
        return


# ======================
# 🤖 AI message handler
# ======================

async def ai_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """If user is in AI mode, send their message to the AI model"""
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id
    user_text = update.message.text.strip()

    # If user is not in AI mode, ignore
    if user_id not in AI_USERS:
        return

    if not openai_client:
        await update.message.reply_text(
            "AI support is currently unavailable. Please try again later."
        )
        return

    try:
        # Show typing indicator
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING,
        )

        response = openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI support assistant for the 'Kaydarap' brand. "
                        "Always respond in the same language as the user. "
                        "Be clear, helpful, and concise."
                    ),
                },
                {"role": "user", "content": user_text},
            ],
        )

        answer = response.choices[0].message.content.strip()
        await update.message.reply_text(answer)

    except Exception as e:
        logger.exception("Error while talking to OpenAI: %s", e)
        await update.message.reply_text(
            "Something went wrong while talking to the AI. Please try again in a few minutes 🙏"
        )


# ======================
# 🚀 Run bot
# ======================

def main() -> None:
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_command))

    # Inline buttons
    app.add_handler(CallbackQueryHandler(callback_handler))

    # All plain text messages (non-commands) → handled by AI if user is in AI mode
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            ai_message_handler,
        )
    )

    logger.info("Kaydarap bot (Instagram + Telegram + AI Support) is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
