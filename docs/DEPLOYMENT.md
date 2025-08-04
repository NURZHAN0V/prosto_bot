# 🚀 Руководство по развертыванию Telegram Greeting Bot

## 📋 Предварительные требования

### Системные требования
- **Python 3.8+** - Основной язык программирования
- **Git** - Система контроля версий
- **pip** - Менеджер пакетов Python
- **Доступ к интернету** - Для работы с Telegram API

### Telegram требования
- **Аккаунт в Telegram** - Для создания бота
- **Доступ к @BotFather** - Для получения токена

## 🔧 Локальная установка

### Шаг 1: Клонирование репозитория
```bash
git clone <repository-url>
cd prosto_bot
```

### Шаг 2: Создание виртуального окружения
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Шаг 3: Установка зависимостей
```bash
pip install -r requirements.txt
```

### Шаг 4: Создание бота в Telegram

1. **Откройте Telegram** и найдите @BotFather
2. **Отправьте команду** `/newbot`
3. **Введите имя бота** (например: "Greeting Bot")
4. **Введите username** (например: "greeting_bot_123")
5. **Сохраните токен** - он понадобится для настройки

### Шаг 5: Настройка переменных окружения

Создайте файл `.env` в корне проекта:
```env
TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
```

### Шаг 6: Запуск бота
```bash
python main.py
```

## ☁️ Развертывание на сервере

### Вариант 1: VPS (Ubuntu/Debian)

#### Подготовка сервера
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и pip
sudo apt install python3 python3-pip python3-venv git -y

# Создание пользователя для бота
sudo adduser botuser
sudo usermod -aG sudo botuser
```

#### Установка бота
```bash
# Переключение на пользователя бота
sudo su - botuser

# Клонирование репозитория
git clone <repository-url>
cd prosto_bot

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Создание файла конфигурации
nano .env
# Добавьте: TELEGRAM_BOT_TOKEN=your_token_here
```

#### Настройка systemd сервиса
```bash
# Создание файла сервиса
sudo nano /etc/systemd/system/greeting-bot.service
```

Содержимое файла:
```ini
[Unit]
Description=Telegram Greeting Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/prosto_bot
Environment=PATH=/home/botuser/prosto_bot/venv/bin
ExecStart=/home/botuser/prosto_bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Запуск сервиса
```bash
# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение автозапуска
sudo systemctl enable greeting-bot

# Запуск сервиса
sudo systemctl start greeting-bot

# Проверка статуса
sudo systemctl status greeting-bot
```

### Вариант 2: Docker

#### Создание Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

#### Создание docker-compose.yml
```yaml
version: '3.8'

services:
  greeting-bot:
    build: .
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
```

#### Запуск с Docker
```bash
# Создание .env файла
echo "TELEGRAM_BOT_TOKEN=your_token_here" > .env

# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f
```

### Вариант 3: Heroku

#### Подготовка приложения
```bash
# Создание Procfile
echo "worker: python main.py" > Procfile

# Создание runtime.txt
echo "python-3.9.18" > runtime.txt
```

#### Развертывание
```bash
# Установка Heroku CLI
# Создание приложения
heroku create your-bot-name

# Установка переменных окружения
heroku config:set TELEGRAM_BOT_TOKEN=your_token_here

# Развертывание
git add .
git commit -m "Initial deployment"
git push heroku main

# Запуск worker процесса
heroku ps:scale worker=1
```

## 🔍 Мониторинг и логирование

### Настройка логирования
```python
# В main.py уже настроено логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
```

### Просмотр логов
```bash
# Systemd сервис
sudo journalctl -u greeting-bot -f

# Docker
docker-compose logs -f

# Heroku
heroku logs --tail
```

## 🔒 Безопасность

### Рекомендации по безопасности
1. **Никогда не коммитьте токены** в репозиторий
2. **Используйте переменные окружения** для конфиденциальных данных
3. **Ограничьте доступ** к серверу только необходимыми портами
4. **Регулярно обновляйте** зависимости
5. **Мониторьте логи** на предмет подозрительной активности

### Настройка firewall (Ubuntu)
```bash
# Установка UFW
sudo apt install ufw

# Настройка правил
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# Включение firewall
sudo ufw enable
```

## 📊 Мониторинг производительности

### Системные метрики
```bash
# Мониторинг CPU и памяти
htop

# Мониторинг дискового пространства
df -h

# Мониторинг сетевой активности
iftop
```

### Логирование ошибок
```python
# Добавьте в main.py для расширенного логирования
import logging.handlers

# Настройка ротации логов
handler = logging.handlers.RotatingFileHandler(
    'bot.log', maxBytes=1024*1024, backupCount=5
)
logger.addHandler(handler)
```

## 🔄 Обновление бота

### Автоматическое обновление
```bash
# Создание скрипта обновления
cat > update_bot.sh << 'EOF'
#!/bin/bash
cd /home/botuser/prosto_bot
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart greeting-bot
EOF

chmod +x update_bot.sh
```

### Ручное обновление
```bash
# Остановка сервиса
sudo systemctl stop greeting-bot

# Обновление кода
git pull origin main

# Обновление зависимостей
source venv/bin/activate
pip install -r requirements.txt

# Запуск сервиса
sudo systemctl start greeting-bot
```

## 🚨 Устранение неполадок

### Частые проблемы

#### 1. Бот не отвечает
```bash
# Проверка статуса сервиса
sudo systemctl status greeting-bot

# Проверка логов
sudo journalctl -u greeting-bot -n 50

# Проверка токена
echo $TELEGRAM_BOT_TOKEN
```

#### 2. Ошибки подключения
```bash
# Проверка интернет-соединения
ping 8.8.8.8

# Проверка DNS
nslookup api.telegram.org

# Проверка портов
netstat -tulpn | grep :443
```

#### 3. Проблемы с зависимостями
```bash
# Пересоздание виртуального окружения
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📞 Поддержка

### Полезные команды
```bash
# Проверка версии Python
python --version

# Проверка установленных пакетов
pip list

# Проверка переменных окружения
env | grep TELEGRAM

# Проверка прав доступа
ls -la .env
```

### Контакты для поддержки
- **Документация**: README.md
- **Логи**: /var/log/ или docker logs
- **Конфигурация**: .env файл

---

**Следуйте этим инструкциям для успешного развертывания вашего Telegram бота!** 