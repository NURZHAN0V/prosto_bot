import logging
import os
from datetime import datetime
from typing import Optional

# Попытка загрузить переменные из .env файла
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    filters, 
    ContextTypes
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class GreetingBot:
    """Телеграм бот для приветствия пользователей по имени"""
    
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Настройка обработчиков команд и сообщений"""
        # Обработчики команд
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("greet", self.greet_command))
        
        # Обработчик текстовых сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Обработчик callback запросов
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Обработчик ошибок
        self.application.add_error_handler(self.error_handler)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        current_time = datetime.now().strftime("%H:%M")
        
        # Создаем красивую клавиатуру
        keyboard = [
            [
                InlineKeyboardButton("👋 Поздороваться", callback_data="greet"),
                InlineKeyboardButton("ℹ️ Помощь", callback_data="help")
            ],
            [
                InlineKeyboardButton("🌅 Доброе утро", callback_data="morning"),
                InlineKeyboardButton("🌆 Добрый вечер", callback_data="evening")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = f"""
🌟 *Добро пожаловать, {user.first_name}!*

Я бот для приветствий! 🤖

🕐 Сейчас: {current_time}

Выберите действие или просто напишите мне своё имя, и я поздороваюсь с вами! ✨
        """.strip()
        
        await update.message.reply_text(
            welcome_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
📚 *Доступные команды:*

/start - Запустить бота
/help - Показать эту справку
/greet [имя] - Поздороваться с указанным именем

💡 *Как использовать:*
• Просто напишите своё имя в чат
• Используйте команду /greet с именем
• Нажмите кнопки в меню

🎨 *Особенности:*
• Красивые приветствия
• Разные варианты приветствий
• Адаптивный интерфейс
        """.strip()
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def greet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /greet"""
        if context.args:
            name = " ".join(context.args)
            await self._send_greeting(update, context, name)
        else:
            await update.message.reply_text(
                "❌ Пожалуйста, укажите имя после команды.\n"
                "Пример: /greet Иван"
            )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        text = update.message.text.strip()
        
        # Если сообщение похоже на имя (не содержит цифр и специальных символов)
        if text and len(text) <= 50 and text.replace(' ', '').isalpha():
            await self._send_greeting(update, context, text)
        else:
            await update.message.reply_text(
                "👋 Привет! Напишите мне своё имя, и я поздороваюсь с вами! ✨"
            )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        current_time = datetime.now().hour
        
        if query.data == "greet":
            await self._send_greeting(update, context, user.first_name)
        elif query.data == "help":
            await self.help_command(update, context)
        elif query.data == "morning":
            greeting = self._get_time_based_greeting(current_time, "утро")
            await query.edit_message_text(
                f"{greeting}, {user.first_name}! 🌅\n\nХорошего дня! ✨",
                parse_mode='Markdown'
            )
        elif query.data == "evening":
            greeting = self._get_time_based_greeting(current_time, "вечер")
            await query.edit_message_text(
                f"{greeting}, {user.first_name}! 🌆\n\nПриятного вечера! ✨",
                parse_mode='Markdown'
            )
    
    async def _send_greeting(self, update: Update, context: ContextTypes.DEFAULT_TYPE, name: str):
        """Отправка приветствия с именем"""
        current_time = datetime.now().hour
        greeting = self._get_time_based_greeting(current_time)
        
        # Создаем красивое приветствие
        greeting_text = f"""
{greeting}, *{name}*! ✨

🎉 Рад вас видеть!
🕐 Время: {datetime.now().strftime("%H:%M")}
📅 Дата: {datetime.now().strftime("%d.%m.%Y")}

Желаю вам отличного дня! 🌟
        """.strip()
        
        # Создаем клавиатуру для дополнительных действий
        keyboard = [
            [
                InlineKeyboardButton("🔄 Ещё раз", callback_data="greet"),
                InlineKeyboardButton("🌅 Утреннее", callback_data="morning")
            ],
            [
                InlineKeyboardButton("🌆 Вечернее", callback_data="evening"),
                InlineKeyboardButton("ℹ️ Помощь", callback_data="help")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                greeting_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                greeting_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    def _get_time_based_greeting(self, hour: int, time_type: Optional[str] = None) -> str:
        """Получение приветствия в зависимости от времени суток"""
        if time_type == "утро":
            return "Доброе утро"
        elif time_type == "вечер":
            return "Добрый вечер"
        
        if 5 <= hour < 12:
            return "Доброе утро"
        elif 12 <= hour < 17:
            return "Добрый день"
        elif 17 <= hour < 23:
            return "Добрый вечер"
        else:
            return "Доброй ночи"
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ошибок"""
        logger.error(f"Произошла ошибка: {context.error}")
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Произошла ошибка. Попробуйте позже или обратитесь к администратору."
            )
    
    def run(self):
        """Запуск бота"""
        logger.info("🚀 Запуск бота...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Главная функция"""
    # Получаем токен из переменной окружения или запрашиваем у пользователя
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("🤖 Telegram Greeting Bot")
        print("=" * 30)
        print("❌ Токен бота не найден!")
        print()
        print("📋 Для получения токена:")
        print("1. Откройте Telegram")
        print("2. Найдите @BotFather")
        print("3. Отправьте команду /newbot")
        print("4. Следуйте инструкциям")
        print("5. Скопируйте полученный токен")
        print()
        print("🔧 Затем создайте файл .env в корне проекта:")
        print("TELEGRAM_BOT_TOKEN=ваш_токен_здесь")
        print()
        print("💡 Или введите токен прямо сейчас:")
        
        token = input("Введите токен бота: ").strip()
        
        if not token or token == "your_bot_token_here":
            print("❌ Токен не введен. Запуск прерван.")
            return
    
    # Создаем и запускаем бота
    try:
        bot = GreetingBot(token)
        print("🚀 Бот запускается...")
        bot.run()
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        print("💡 Проверьте правильность токена")

if __name__ == '__main__':
    main()
