import logging
import os
from dotenv import load_dotenv
load_dotenv()
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, filters, ContextTypes
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "877070118"))

TOUR, NAME, CONTACT = range(3)

TOURS = [
    "🔺 Дахшур — Тур выходного дня (май 2026)",
    "🏛 Люксор — Карнак, храм Тота и Исиды",
    "🌊 Эдфу и Дендера — Хорус и Хатхор",
    "⚡️ Асуан — Храм Исиды",
    "🌿 Асьют — Монастырь. Женская сила горы",
    "📋 Хочу узнать обо всех турах",
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    keyboard = [[t] for t in TOURS]
    await update.message.reply_text(
        "✦\n\nДобро пожаловать в *Anima Sacra*\n\n"
        "_Места, которые помнит твоя душа_\n\n"
        "Какое направление тебя притягивает?",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return TOUR


async def tour_chosen(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["tour"] = update.message.text
    await update.message.reply_text(
        "Прекрасный выбор ✦\n\nКак тебя зовут?",
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME


async def name_received(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["name"] = update.message.text
    await update.message.reply_text(
        f"Рада познакомиться, {update.message.text} ✦\n\n"
        "Оставь свой контакт для связи:\n"
        "_Telegram @username или номер WhatsApp_",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return CONTACT


async def contact_received(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["contact"] = update.message.text
    user = update.effective_user
    d = ctx.user_data

    admin_text = (
        "✦ *Новая заявка — Anima Sacra* ✦\n\n"
        f"👤 *Имя:* {d.get('name')}\n"
        f"🏛 *Тур:* {d.get('tour')}\n"
        f"📞 *Контакт:* {d.get('contact')}\n\n"
        f"📱 *Telegram:* @{user.username or '—'} (`{user.id}`)"
    )

    try:
        await ctx.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="Markdown")
        logger.info(f"Заявка отправлена администратору {ADMIN_ID}")
    except Exception as e:
        logger.error(f"Ошибка отправки заявки: {e}")

    await update.message.reply_text(
        f"✦\n\n{d.get('name')}, твоя заявка принята.\n\n"
        "Я напишу тебе в ближайшее время ✦\n\n"
        "_Места, которые помнит твоя душа, уже ждут_",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Хорошо ✦ Если захочешь вернуться — просто напиши /start",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            TOUR:    [MessageHandler(filters.TEXT & ~filters.COMMAND, tour_chosen)],
            NAME:    [MessageHandler(filters.TEXT & ~filters.COMMAND, name_received)],
            CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, contact_received)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv)
    logger.info("Anima Sacra бот запущен ✦")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
