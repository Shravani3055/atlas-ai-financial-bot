import os
import re
import asyncio
import traceback

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from database import create_tables
from gemini_service import ask_gemini
from finance_service import check_budget_alert

from memory import (
    create_user,
    update_name,
    update_allowance,
    get_user,
    clear_expenses,
    add_expense,
    get_total_spent,
    get_top_category
)

# ================== TOKEN ==================

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN not set")

# ================== COMMANDS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi! I'm Atlas — your AI Financial Assistant.\n"
        "Track spending, set budgets, and get smart advice. 📊"
    )

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    user_data = get_user(telegram_id)

    if not user_data:
        await update.message.reply_text("No profile found.")
        return

    name, allowance = user_data

    await update.message.reply_text(
        f"👤 Profile\n\n"
        f"Name: {name or 'Not set'}\n"
        f"Budget: ₹{allowance if allowance is not None else 'Not set'}"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    clear_expenses(telegram_id)
    await update.message.reply_text("🗑️ All expenses cleared.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start\n/profile\n/reset\n/help\n\n"
        "Examples:\n"
        "budget is 8000\n"
        "spent 300 on food\n"
        "status"
    )

# ================== MAIN CHAT ==================

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    try:
        print("🔥 CHAT TRIGGERED")

        user_message = update.message.text
        msg = user_message.lower()
        telegram_id = update.effective_user.id

        print("📩 User:", user_message)

        create_user(telegram_id)

        # -------- NAME --------
        name_match = re.search(r"(?:my name is|i am)\s+(\w+)", msg)
        if name_match:
            update_name(telegram_id, name_match.group(1).capitalize())

        user_data = get_user(telegram_id)
        name, allowance = (user_data if user_data else (None, None))

        # -------- STATUS --------
        if any(word in msg for word in ["status", "summary", "report"]):
            total_spent = get_total_spent(telegram_id)
            remaining = allowance - total_spent if allowance else None
            top_category = get_top_category(telegram_id)

            await update.message.reply_text(
                f"📊 Status\n\n"
                f"Budget: ₹{allowance}\n"
                f"Spent: ₹{total_spent}\n"
                f"Remaining: ₹{remaining}\n"
                f"Top category: {top_category}"
            )
            return

        # -------- SET BUDGET --------
        if "budget" in msg:
            match = re.search(r"(\d+)", msg)
            if match:
                amount = int(match.group(1))
                update_allowance(telegram_id, amount)
                await update.message.reply_text(f"💰 Budget set: ₹{amount}")
                return

        # -------- EXPENSE --------
        spend_matches = re.findall(
            r"(?:spent|pay|paid|bought)\s*(\d+)\s*(?:on\s*(\w+))?",
            msg
        )

        if spend_matches:
            for amount, category in spend_matches:
                add_expense(telegram_id, int(amount), category or "general")

            total_spent = get_total_spent(telegram_id)
            remaining = allowance - total_spent if allowance else None

            await update.message.reply_text(
                f"💸 Total spent: ₹{total_spent}\nRemaining: ₹{remaining}"
            )

            alert = check_budget_alert(total_spent, allowance)
            if alert:
                await update.message.reply_text(alert)

            return

        # ================= AI FALLBACK =================
        print("🤖 Going to Gemini...")

        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING,
        )

        # ⚠️ SAFE CALL (THIS FIXES YOUR CRASH)
        loop = asyncio.get_running_loop()
        reply = await loop.run_in_executor(
            None,
            ask_gemini,
            user_message  # KEEP SIMPLE (no context for now)
        )

        print("✅ Gemini reply:", reply)

        if not reply:
            reply = "⚠️ AI gave empty response"

        await update.message.reply_text(reply)

    except Exception as e:
        print("❌ FULL ERROR:")
        traceback.print_exc()

        await update.message.reply_text(f"❌ Error:\n{str(e)}")

# ================== MAIN ==================

def main():
    create_tables()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("help", help_command))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("🤖 Bot running...")
    app.run_polling()

# ================== ENTRY ==================

if __name__ == "__main__":
    main()