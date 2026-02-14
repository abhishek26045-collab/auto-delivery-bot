import os
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("8393684527:AAFimC-SeiYAHmxdTbgS7n_mH18Yj7kR81A")

app = Flask(__name__)
telegram_app = ApplicationBuilder().token(TOKEN).build()

# 🔹 Product Delivery
async def deliver_product(chat_id, context):
    try:
        with open("products.txt", "r") as f:
            products = f.readlines()

        if not products:
            await context.bot.send_message(chat_id=chat_id, text="❌ Out of stock.")
            return

        product = products[0].strip()

        with open("products.txt", "w") as f:
            f.writelines(products[1:])

        await context.bot.send_message(chat_id=chat_id, text=f"✅ Your Product:\n{product}")

    except:
        await context.bot.send_message(chat_id=chat_id, text="Error delivering product.")

# 🔹 Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Buy Now 💳", callback_data="buy")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome! Click below to buy.", reply_markup=reply_markup)

# 🔹 Button Handler
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await deliver_product(query.from_user.id, context)

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button))

@app.route("/")
def home():
    return "Bot is running!"

if __name__ == "__main__":
    telegram_app.run_polling()
