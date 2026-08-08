import re
import asyncio
import traceback

from finance_service import check_budget_alert

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import TELEGRAM_BOT_TOKEN
from database import create_tables
from gemini_service import ask_gemini

from memory import (
    create_user,
    update_name,
    update_allowance,
    get_user,
    update_conversation,
    clear_expenses,
    add_expense,
    get_total_spent,
    get_top_category
)

# ✅ START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi! I'm Atlas — your AI Financial Assistant.\n"
        "Track spending, set budgets, and get smart advice. 📊"
    )

# ✅ PROFILE
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

# ✅ RESET
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    clear_expenses(telegram_id)
    await update.message.reply_text("🗑️ All expenses cleared.")

# ✅ HELP
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start\n/profile\n/reset\n/help\n\n"
        "Examples:\n"
        "budget is 8000\n"
        "spent 300 on food\n"
        "added 500\n"
        "status"
    )

# ✅ MAIN CHAT
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_message = update.message.text
    msg = user_message.lower()
    telegram_id = update.effective_user.id

    create_user(telegram_id)

    # 🔹 START FRESH
    if "start fresh" in msg:
        clear_expenses(telegram_id)
        await update.message.reply_text("🔄 Starting fresh. All expenses cleared.")
        return

    # 🔹 NAME
    name_match = re.search(r"(?:my name is|i am)\s+(\w+)", msg)
    if name_match:
        update_name(telegram_id, name_match.group(1).capitalize())

    user_data = get_user(telegram_id)
    name, allowance = (user_data if user_data else (None, None))

    # 🔹 STATUS
    if any(word in msg for word in ["status", "summary", "report"]):
        total_spent = get_total_spent(telegram_id)
        remaining = allowance - total_spent if allowance is not None else None
        top_category = get_top_category(telegram_id)

        await update.message.reply_text(
            f"📊 Status\n\n"
            f"Budget: ₹{allowance}\n"
            f"Spent: ₹{total_spent}\n"
            f"Remaining: ₹{remaining if remaining is not None else 'unknown'}\n"
            f"Top category: {top_category if top_category else 'N/A'}"
        )
        return

    # 🔹 ADD TO BUDGET
    add_budget_match = re.search(r"(?:add|added|increase)\s*(\d+)", msg)
    if add_budget_match:
        amount = int(add_budget_match.group(1))

        if allowance is not None:
            new_budget = allowance + amount
            update_allowance(telegram_id, new_budget)
            await update.message.reply_text(f"💰 New budget: ₹{new_budget}")
        else:
            await update.message.reply_text("⚠️ Set budget first")
        return

    # 🔹 SET BUDGET
    if "budget" in msg:
        match = re.search(r"(\d+)", msg)
        if match:
            amount = int(match.group(1))
            update_allowance(telegram_id, amount)
            await update.message.reply_text(f"💰 Budget set: ₹{amount}")
            return

    # 🔹 INCOME
    income_match = re.search(r"(?:got|received|earned)\s*(\d+)", msg)
    if income_match:
        amount = int(income_match.group(1))

        if allowance is not None:
            new_budget = allowance + amount
            update_allowance(telegram_id, new_budget)
            await update.message.reply_text(f"💰 New budget: ₹{new_budget}")
        else:
            await update.message.reply_text("⚠️ Set budget first")
        return

    # 🔹 EXPENSE
    spend_matches = re.findall(
        r"(?:spent|pay|paid|bought)\s*(\d+)\s*(?:on\s*(\w+))?",
        msg
    )

    if spend_matches:
        for amount, category in spend_matches:
            add_expense(telegram_id, int(amount), category or "general")

        total_spent = get_total_spent(telegram_id)
        remaining = allowance - total_spent if allowance is not None else None

        await update.message.reply_text(
            f"💸 Total spent: ₹{total_spent}\nRemaining: ₹{remaining}"
        )

        # 🔥 ALERT
        alert = check_budget_alert(total_spent, allowance)
        if alert:
            await update.message.reply_text(alert)

        # 🔹 TOP CATEGORY
        top_category = get_top_category(telegram_id)
        if top_category:
            await update.message.reply_text(
                f"📊 Most spending on: {top_category.upper()}"
            )

        return

    # 🔹 AI RESPONSE
    total_spent = get_total_spent(telegram_id)
    remaining = allowance - total_spent if allowance is not None else None

    context_message = f"""
Budget: {allowance}
Spent: {total_spent}
Remaining: {remaining}

User: {user_message}
"""

    try:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING,
        )

        reply = await asyncio.to_thread(ask_gemini, context_message)
        update_conversation(telegram_id, user_message)

        await update.message.reply_text(reply)

    except Exception:
        traceback.print_exc()
        await update.message.reply_text("⚠️ Something went wrong")

# ✅ MAIN
def main():
    create_tables()

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("help", help_command))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()