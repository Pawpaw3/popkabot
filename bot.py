import logging
import os
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import instaloader

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN provided")

# Инициализируем Instaloader
L = instaloader.Instaloader()

# Функция для обработки команд /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Привет! Я бот, который проверяет ссылки на Instagram и отправляет видео, если они содержат видео.'
    )

# Функция для обработки сообщений с ссылками на Instagram
async def handle_instagram_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    logger.info(f"Обнаружена ссылка на Instagram: {url}")

    try:
        # Загружаем пост из Instagram
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(L.context, shortcode)

        if post.is_video:
            video_url = post.video_url
            logger.info(f"Видео URL: {video_url}")

            # Отправляем видео в чат
            await update.message.reply_video(video=video_url)
        else:
            logger.info("Ссылка не содержит видео.")
            # Ничего не отправляем, если ссылка не содержит видео.

    except instaloader.exceptions.InstaloaderException as e:
        logger.error(f"Ошибка при обработке ссылки: {e}")
        await update.message.reply_text("Произошла ошибка при обработке ссылки. Пожалуйста, попробуйте позже.")
        # Подождите перед повторной попыткой запроса
        time.sleep(60)

def main() -> None:
    # Создаем Application и передаем ему токен бота
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex(r'(https?://www\.instagram\.com/\S+)'), handle_instagram_link))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
