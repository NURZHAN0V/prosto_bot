module.exports = {
  apps: [
    {
      name: 'telegram-greeting-bot',
      script: 'main.py',
      interpreter: 'venv\\Scripts\\python.exe',
      autorestart: true,
      watch: false,
      env: {
        TELEGRAM_BOT_TOKEN: process.env.TELEGRAM_BOT_TOKEN || 'your_bot_token_here'
      }
    }
  ]
};