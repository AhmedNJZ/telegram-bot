from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters
from dotenv import load_dotenv
from groq import Groq
import os

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are Sky, a helpful sales agent for Innovation City — a free zone in Ras Al Khaimah, UAE.
You help businesses and entrepreneurs with:
- Company setup costs and packages
- Business activities and choosing the right one
- Office requirements (physical, flexi desk, or remote)
- General questions about setting up in Innovation City

Be professional, friendly, and concise. Always answer in the language the user writes in.
"""

# Store conversation history per user
conversations = {}

async def start(update, context):
    conversations[update.message.chat_id] = []
    await update.message.reply_text(
        "Good day! I'm Sky, your Innovation City sales agent. How can I help you today?\n\n"
        "You can ask me about:\n"
        "• Company setup costs\n"
        "• Business activities\n"
        "• Office requirements"
    )

async def reply(update, context):
    chat_id = update.message.chat_id
    user_message = update.message.text

    # Initialize history if new user
    if chat_id not in conversations:
        conversations[chat_id] = []

    # Add user message to history
    conversations[chat_id].append({
        "role": "user",
        "content": user_message
    })

    # Send "typing..." indicator
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    # Call Groq
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversations[chat_id],
        temperature=0.7,
    )

    bot_reply = response.choices[0].message.content

    # Add bot reply to history
    conversations[chat_id].append({
        "role": "assistant",
        "content": bot_reply
    })

    await update.message.reply_text(bot_reply)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, reply))

print("Sky bot is running...")
app.run_polling()