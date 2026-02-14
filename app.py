import os
import razorpay
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("8419934959:AAFcPs4dK6LsvPjpwz6IhB_BJKU2TMCuU4M")
RAZORPAY_KEY_ID = os.getenv("rzp_test_SG110UyUiDLEGk")
RAZORPAY_KEY_SECRET = os.getenv("h6kP7aG1ir29cxLcj1H0wsx3")
WEBHOOK_SECRET = os.getenv("srv-d68694k9c44c73fmrdfg")

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
bot = Bot(8419934959:AAFcPs4dK6LsvPjpwz6IhB_BJKU2TMCuU4M)
app = Flask(__name__)

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Buy Now 💳", callback_data="buy")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Click below to buy product.", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    amount = 100  # ₹1 test payment
    order = client.order.create(dict(amount=amount, currency="INR", payment_capture='1'))

    user_data[order["id"]] = query.from_user.id
    payment_link = f"https://rzp.io/l/{order['id']}"

    await query.message.reply_text(f"Pay here:\n{payment_link}")

def deliver_product(user_id):
    with open("products.txt", "r") as f:
        products = f.readlines()

    if not products:
        bot.send_message(chat_id=user_id, text="Out of stock.")
        return

    product = products[0].strip()

    with open("products.txt", "w") as f:
        f.writelines(products[1:])

    bot.send_message(chat_id=user_id, text=f"Your Product Key:\n{product}")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    received_signature = request.headers.get("X-Razorpay-Signature")

    try:
        client.utility.verify_webhook_signature(
            request.data,
            received_signature,
            WEBHOOK_SECRET
        )
    except:
        return "Invalid signature", 400

    if data["event"] == "payment.captured":
        order_id = data["payload"]["payment"]["entity"]["order_id"]

        if order_id in user_data:
            user_id = user_data[order_id]
            deliver_product(user_id)

    return "OK", 200

telegram_app = ApplicationBuilder().token(TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button_handler))

if __name__ == "__main__":
    telegram_app.run_polling()
