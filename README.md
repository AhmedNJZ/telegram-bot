# Innovation City Telegram Bot
A Telegram chatbot that acts as Sky, an AI sales agent for Innovation City free zone in Ras Al Khaimah, UAE.

## What it does
- Answers questions about company setup costs and packages
- Explains available business activities
- Guides users on office requirements
- Remembers conversation history per user
- Shows typing indicator while generating a response

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/AhmedNJZ/telegram-bot.git
cd telegram-bot
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create a .env file
BOT_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key

- Get a free Telegram bot token from @BotFather on Telegram
- Get a free Groq API key at https://console.groq.com

### 5. Run the bot
```bash
python bot.py
```
