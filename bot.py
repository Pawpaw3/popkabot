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

# Чтение учетных данных из переменных окружения
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD')

# Выводим все переменные окружения для отладки
logger.info(f"Environment Variables: {os.environ}")
logger.info(f"INSTAGRAM_USERNAME: {INSTAGRAM_USERNAME}")
logger.info(f"INSTAGRAM_PASSWORD: {INSTAGRAM_PASSWORD}")

if not INSTAGRAM_USERNAME or not INSTAGRAM_PASSWORD:
    raise ValueError("Instagram credentials are not set")

# Инициализируем Instaloader и авторизуемся в Instagram
L = instaloader.Instaloader()
try:
    L.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
except instaloader.exceptions.BadCredentialsException:
    logger.error("Invalid credentials. Please check your username and password.")
    raise
except Exception as e:
    logger.error(f"An error occurred while logging in: {e}")
    raise

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

        # Добавляем паузу между запросами
        time.sleep(5)

    except instaloader.exceptions.InstaloaderException as e:
        logger.error(f"Ошибка при обработке ссылки: {e}")
        # Ничего не отправляем в случае ошибки.

def main() -> None:
    # Создаем Application и передаем ему токен бота
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex(r'https?://(www\.)?instagram\.com/\S+'), handle_instagram_link))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
