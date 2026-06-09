from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters
from dotenv import load_dotenv
import os
import requests

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")

API_BASE_URL = "https://proc-sales-agent-impl-7a2j52.2ky31l-1.deu-c1.eu1.cloudhub.io/api/chat"

# Store session IDs per Telegram user
sessions = {}

async def start(update, context):
    chat_id = update.message.chat_id
    # Clear any existing session to start fresh
    sessions.pop(chat_id, None)
    await update.message.reply_text(
        "Hello! I'm Sky, your Innovation City sales agent.\n\nHow can I help you today?"
    )

async def reply(update, context):
    chat_id = update.message.chat_id
    user_message = update.message.text

    # Show typing indicator
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    # Build request payload
    payload = {"message": user_message}

    # Include session ID if we have one
    if chat_id in sessions:
        payload["sessionId"] = sessions[chat_id]

    try:
        response = requests.post(API_BASE_URL, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()

        # Save session ID for conversation continuity
        sessions[chat_id] = data["sessionId"]

        bot_reply = data["reply"]

        # If lead was submitted, notify the user
        if data.get("leadSubmitted"):
            bot_reply += "\n\n✅ Your details have been submitted. Our team will be in touch shortly!"

        await update.message.reply_text(bot_reply)

    except requests.exceptions.Timeout:
        await update.message.reply_text("Sorry, the request timed out. Please try again.")
    except requests.exceptions.ConnectionError:
        await update.message.reply_text("Sorry, I couldn't connect to the server. Please try again later.")
    except Exception as e:
        await update.message.reply_text("Sorry, something went wrong. Please try again.")
        import traceback
traceback.print_exc()
print(f"Error: {e}")

async def reset(update, context):
    chat_id = update.message.chat_id
    sessions.pop(chat_id, None)
    await update.message.reply_text("Session reset. Starting fresh — how can I help you?")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(MessageHandler(filters.TEXT, reply))

print("Innovation City bot is running...")
app.run_polling()