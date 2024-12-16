import os
from flask import Flask, request, jsonify
import stripe
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Initialize OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

class FatherBot:
    def __init__(self):
        self.answers_per_payment = 5  # Number of answers per payment
        self.price_per_bundle = 1000  # Price in cents ($10.00)
        self.user_credits = {}  # Track user credits

    def create_payment_intent(self, customer_email):
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=self.price_per_bundle,
                currency='usd',
                payment_method_types=['card'],
                metadata={'customer_email': customer_email}
            )
            return payment_intent.client_secret
        except Exception as e:
            return str(e)

    def process_payment_success(self, customer_email):
        if customer_email not in self.user_credits:
            self.user_credits[customer_email] = 0
        self.user_credits[customer_email] += self.answers_per_payment

    def get_answer(self, customer_email, question):
        if customer_email not in self.user_credits or self.user_credits[customer_email] <= 0:
            return {"error": "No credits available. Please purchase more answers."}
        
        try:
            # Use OpenAI to generate fatherly advice
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a wise and caring father figure providing advice and guidance."},
                    {"role": "user", "content": question}
                ]
            )
            
            self.user_credits[customer_email] -= 1
            return {
                "answer": response.choices[0].message.content,
                "credits_remaining": self.user_credits[customer_email]
            }
        except Exception as e:
            return {"error": str(e)}

# Initialize bot
father_bot = FatherBot()

@app.route('/create-payment-intent', methods=['POST'])
def create_payment():
    data = request.json
    client_secret = father_bot.create_payment_intent(data.get('email'))
    return jsonify({'clientSecret': client_secret})

@app.route('/payment-success', methods=['POST'])
def payment_success():
    data = request.json
    father_bot.process_payment_success(data.get('email'))
    return jsonify({'status': 'success'})

@app.route('/get-answer', methods=['POST'])
def get_answer():
    data = request.json
    response = father_bot.get_answer(data.get('email'), data.get('question'))
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True) 