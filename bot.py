from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from telegram import Update
from dotenv import load_dotenv
from groq import Groq
import os
import requests

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
SALES_API_URL = os.environ.get("SALES_AGENT_API_BASE_URL", "")

# ==========================================
# CONFIGURATION
# ==========================================

SYSTEM_PROMPTS = {
    "english": """You are Sky, a professional and friendly sales agent for Innovation City — a free zone in Ras Al Khaimah, UAE.
You help businesses and entrepreneurs with company setup, licensing, visas, office requirements, and packages.
Be concise, helpful, and professional. Always respond in English.""",

    "arabic": """أنت سكاي، وكيل مبيعات محترف وودود لمدينة الابتكار — منطقة حرة في رأس الخيمة، الإمارات العربية المتحدة.
تساعد الشركات ورجال الأعمال في إعداد الشركات والتراخيص والتأشيرات ومتطلبات المكاتب والحزم.
كن موجزاً ومفيداً ومحترفاً. أجب دائماً باللغة العربية.""",

    "hindi": """आप Sky हैं, Innovation City के लिए एक पेशेवर और मित्रवत बिक्री एजेंट — रास अल खैमाह, UAE में एक फ्री ज़ोन।
आप व्यवसाय स्थापना, लाइसेंसिंग, वीज़ा, कार्यालय आवश्यकताओं और पैकेजों में मदद करते हैं।
संक्षिप्त, सहायक और पेशेवर रहें। हमेशा हिंदी में जवाब दें।"""
}

INFORMATION_TOPICS = {
    "licensing": "business licenses available at Innovation City including Freelancer License, FZ-LLC, and Branch License",
    "gaming": "gaming and esports business opportunities at Innovation City",
    "visa": "UAE visa requirements and process for business owners at Innovation City",
    "setup cost": "company setup costs and fees at Innovation City",
    "packages": "available packages at Innovation City including flexi desk, shared office, and physical office",
    "contact": "Innovation City contact information and how to get in touch with the team",
}

# Store sessions and language preferences per user
conversations = {}
user_languages = {}

# ==========================================
# HELPERS
# ==========================================

def get_system_prompt(chat_id):
    lang = user_languages.get(chat_id, "english")
    return SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS["english"])

def check_api_status():
    if not SALES_API_URL:
        return "unknown"
    try:
        response = requests.post(
            f"{SALES_API_URL}/api/chat",
            json={"message": "ping"},
            timeout=5
        )
        if response.status_code == 200:
            return "online"
        elif response.status_code >= 500:
            return "degraded"
        else:
            return "degraded"
    except requests.exceptions.Timeout:
        return "degraded"
    except Exception:
        return "offline"

async def ask_sky(chat_id, question):
    if chat_id not in conversations:
        conversations[chat_id] = []

    conversations[chat_id].append({
        "role": "user",
        "content": question
    })

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": get_system_prompt(chat_id)}] + conversations[chat_id],
        temperature=0.7,
    )

    bot_reply = response.choices[0].message.content

    conversations[chat_id].append({
        "role": "assistant",
        "content": bot_reply
    })

    return bot_reply

# ==========================================
# COMMANDS
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    conversations[chat_id] = []
    await update.message.reply_text(
        "👋 Welcome to Innovation City!\n\n"
        "I'm *Sky*, your AI sales agent. I can help you with:\n"
        "• Company setup and licensing\n"
        "• Packages and pricing\n"
        "• UAE visa requirements\n"
        "• Office options\n\n"
        "You can talk to me directly or use commands.\n"
        "Type *!help* to see all available commands.",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Sky Bot Commands*\n\n"
        "*General*\n"
        "`!start` — Welcome message\n"
        "`!help` — Show this list\n"
        "`!status` — Check if Sky is operational\n\n"
        "*Ask Sky*\n"
        "`!ask [question]` — Ask Sky anything\n"
        "Example: `!ask What licenses are available?`\n\n"
        "*Information*\n"
        "`!information [topic]` — Get info on a topic\n"
        "Topics: `licensing`, `gaming`, `visa`, `setup cost`, `packages`, `contact`\n\n"
        "*Language*\n"
        "`!language [language]` — Change response language\n"
        "Options: `english`, `arabic`, `hindi`\n\n"
        "*Session*\n"
        "`!reset` — Start a fresh conversation\n",
        parse_mode="Markdown"
    )

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    question = " ".join(context.args)

    if not question:
        await update.message.reply_text("Please provide a question.\nExample: `!ask What licenses are available?`", parse_mode="Markdown")
        return

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    reply = await ask_sky(chat_id, question)
    await update.message.reply_text(reply)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.message.chat_id, action="typing")
    state = check_api_status()

    if state == "online":
        msg = "✅ *Sky is Online*\nAll systems operational."
    elif state == "degraded":
        msg = "⚠️ *Sky is Degraded*\nService is experiencing issues."
    elif state == "offline":
        msg = "❌ *Sky is Offline*\nUnable to reach the service."
    else:
        msg = "❓ *Status Unknown*\nNo API URL configured."

    await update.message.reply_text(msg, parse_mode="Markdown")

async def information(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    topic = " ".join(context.args).lower()

    if not topic:
        topics = ", ".join(f"`{t}`" for t in INFORMATION_TOPICS.keys())
        await update.message.reply_text(
            f"Please provide a topic.\nAvailable topics: {topics}",
            parse_mode="Markdown"
        )
        return

    if topic not in INFORMATION_TOPICS:
        topics = ", ".join(f"`{t}`" for t in INFORMATION_TOPICS.keys())
        await update.message.reply_text(
            f"Topic `{topic}` not found.\nAvailable topics: {topics}",
            parse_mode="Markdown"
        )
        return

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    question = f"Tell me about {INFORMATION_TOPICS[topic]} at Innovation City."
    reply = await ask_sky(chat_id, question)
    await update.message.reply_text(reply)

async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    lang = " ".join(context.args).lower()

    supported = list(SYSTEM_PROMPTS.keys())

    if not lang or lang not in supported:
        options = ", ".join(f"`{l}`" for l in supported)
        await update.message.reply_text(
            f"Please provide a language.\nOptions: {options}",
            parse_mode="Markdown"
        )
        return

    user_languages[chat_id] = lang
    await update.message.reply_text(f"✅ Language set to *{lang.capitalize()}*.", parse_mode="Markdown")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    conversations[chat_id] = []
    await update.message.reply_text("🔄 Session reset. Starting fresh — how can I help you?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text

    # Handle ! commands sent as plain messages
    if text.startswith("!"):
        parts = text[1:].split(" ", 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        context.args = args.split() if args else []

        if cmd == "start":
            await start(update, context)
        elif cmd == "help":
            await help_command(update, context)
        elif cmd == "ask":
            await ask(update, context)
        elif cmd == "status":
            await status(update, context)
        elif cmd == "information":
            await information(update, context)
        elif cmd == "language":
            await language(update, context)
        elif cmd == "reset":
            await reset(update, context)
        else:
            await update.message.reply_text(f"Unknown command `!{cmd}`. Type `!help` for available commands.", parse_mode="Markdown")
        return

    # Regular message — send to Sky
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    reply = await ask_sky(chat_id, text)
    await update.message.reply_text(reply)

# ==========================================
# APP
# ==========================================

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("ask", ask))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("information", information))
app.add_handler(CommandHandler("language", language))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(MessageHandler(filters.TEXT, handle_message))

print("Sky bot is running...")
app.run_polling()