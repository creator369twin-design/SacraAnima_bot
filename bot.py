import logging
import os
import asyncio
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, filters, ContextTypes
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8671119609:AAFKVAD8q6ArusJMbdxsjevwBj8lhZqweus")
ADMIN_ID   = int(os.getenv("ADMIN_ID", "877070118"))

TOUR, NAME, SOURCE, COMMENT = range(4)

TOURS = [
    "🏛 Луксор — Карнак и Дендера",
    "🌊 Асуан — Острова Филе и Хейса",
    "⚡️ Эдфу — Храм Гора",
    "🔺 Каир / Дахшур — Первые пирамиды",
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
        "Я помогу тебе узнать о наших турах и оставить заявку.\n\n"
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
    keyboard = [
        ["Instagram"], ["Telegram"],
        ["Рекомендация подруги"], ["Была на туре раньше"], ["Другое"],
    ]
    await update.message.reply_text(
        f"Рада познакомиться, {update.message.text} ✦\n\nОткуда ты узнала об Anima Sacra?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return SOURCE


async def source_received(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["source"] = update.message.text
    await update.message.reply_text(
        "Есть вопрос или что-то важное, что хочешь передать?\n\n"
        "_Напиши — или отправь_ «–» _если всё понятно_",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return COMMENT


async def comment_received(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    comment = update.message.text
    if comment in ("–", "-"):
        comment = "—"
    ctx.user_data["comment"] = comment
    user = update.effective_user
    d = ctx.user_data

    admin_text = (
        "✦ *Новая заявка — Anima Sacra* ✦\n\n"
        f"👤 *Имя:* {d.get('name')}\n"
        f"🏛 *Тур:* {d.get('tour')}\n"
        f"📍 *Откуда:* {d.get('source')}\n"
        f"💬 *Комментарий:* {d.get('comment')}\n\n"
        f"📱 *Telegram:* @{user.username or '—'} (`{user.id}`)"
    )

    try:
        await ctx.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка отправки заявки: {e}")

    await update.message.reply_text(
        f"✦\n\n{d.get('name')}, твоя заявка принята.\n\n"
        "Я напишу тебе в ближайшее время — расскажу о деталях тура, датах и всём что важно знать.\n\n"
        "_Места, которые помнит твоя душа, уже ждут_ ✦",
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


async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            TOUR:    [MessageHandler(filters.TEXT & ~filters.COMMAND, tour_chosen)],
            NAME:    [MessageHandler(filters.TEXT & ~filters.COMMAND, name_received)],
            SOURCE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, source_received)],
            COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, comment_received)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv)
    logger.info("Anima Sacra бот запущен ✦")
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
