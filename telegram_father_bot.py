import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import stripe
from dotenv import load_dotenv
import openai
import json

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Initialize OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

class FatherBot:
    def __init__(self):
        self.answers_per_payment = 5
        self.price_per_bundle = 1000  # Price in cents ($10.00)
        self.user_credits = {}

    def get_user_credits(self, user_id):
        return self.user_credits.get(str(user_id), 0)

    def add_credits(self, user_id):
        user_id = str(user_id)
        if user_id not in self.user_credits:
            self.user_credits[user_id] = 0
        self.user_credits[user_id] += self.answers_per_payment

    def use_credit(self, user_id):
        user_id = str(user_id)
        if self.get_user_credits(user_id) > 0:
            self.user_credits[user_id] -= 1
            return True
        return False

    async def get_answer(self, question):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a wise and caring father figure providing advice and guidance."},
                    {"role": "user", "content": question}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"

# Initialize bot
father_bot = FatherBot()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    welcome_message = (
        f"Hi {user.first_name}! 👋 I'm your AI Father Bot.\n\n"
        "I'm here to provide fatherly advice and guidance.\n"
        "You can purchase 5 answers for $10.\n\n"
        "Available commands:\n"
        "/credits - Check your remaining credits\n"
        "/buy - Purchase more credits\n"
        "Just send me a message to ask for advice!"
    )
    await update.message.reply_text(welcome_message)

async def credits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check remaining credits."""
    user_id = update.effective_user.id
    credits_count = father_bot.get_user_credits(user_id)
    await update.message.reply_text(f"You have {credits_count} answers remaining.")

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initiate the purchase process."""
    keyboard = [
        [InlineKeyboardButton("Pay with Stripe", url=f"https://buy.stripe.com/YOUR_PAYMENT_LINK")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Click below to purchase 5 answers for $10:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages."""
    user_id = update.effective_user.id
    
    if father_bot.get_user_credits(user_id) <= 0:
        await update.message.reply_text(
            "You don't have any credits left. Use /buy to purchase more answers."
        )
        return

    if father_bot.use_credit(user_id):
        question = update.message.text
        answer = await father_bot.get_answer(question)
        credits_left = father_bot.get_user_credits(user_id)
        
        response = f"{answer}\n\nRemaining credits: {credits_left}"
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("You need to purchase credits to ask questions. Use /buy command.")

def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("credits", credits))
    application.add_handler(CommandHandler("buy", buy))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 