import telebot
import requests
import json
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Инициализируем бота
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

# API эндпоинт для нейросети
AI_API_URL = "http://localhost:11434/api/generate"

def ask_ai(prompt):
    """Отправляет запрос к нейросети"""
    # Ограничиваем длину промпта
    if len(prompt) > 1000:
        return "Сообщение слишком длинное (макс. 1000 символов)."
    
    try:
        payload = {
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(AI_API_URL, json=payload, timeout=120)
        response.raise_for_status()
        
        data = response.json()
        return data.get('response', 'Извините, не удалось получить ответ от нейросети.').strip()
    
    except requests.exceptions.Timeout:
        return "⏳ Слишком долго генерируем ответ. Попробуй позже или задай короткий вопрос."
    except requests.exceptions.ConnectionError:
        return "🚫 Не удалось подключиться к Ollama. Проверь, запущен ли сервер."
    except requests.exceptions.RequestException as e:
        return f"❌ Ошибка подключения к нейросети: {str(e)}"
    except json.JSONDecodeError:
        return "Ошибка обработки ответа от нейросети"
    except Exception as e:
        return f"Ошибка обработки: {e}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Обработчик команды /start"""
    welcome_text = """
🤖 Привет! Я бот с нейросетью.

Просто напиши мне сообщение, и я отвечу с помощью AI.

Команды:
/start - показать это сообщение
/help - помощь
    """
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['help'])
def send_help(message):
    """Обработчик команды /help"""
    help_text = """
📚 Как использовать бота:

1. Просто напиши любое сообщение
2. Я отправлю его нейросети Mistral
3. Получу ответ и отправлю тебе

Примеры вопросов:
- "Расскажи анекдот"
- "Что такое Python?"
- "Напиши стихотворение"
    """
    bot.reply_to(message, help_text)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """Обработчик всех остальных сообщений"""
    user_message = message.text
    
    # Отправляем "печатает" статус
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Получаем ответ от нейросети
    ai_response = ask_ai(user_message)
    
    # Отправляем ответ пользователю
    bot.reply_to(message, ai_response)

if __name__ == "__main__":
    print("🤖 Бот запущен...")
    print("Нажмите Ctrl+C для остановки")
    
    try:
        bot.polling(none_stop=True)
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}") 