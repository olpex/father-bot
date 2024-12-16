# Father Bot with Stripe Integration

A wise father figure bot that provides advice and guidance, with a payment system using Stripe.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
- Copy `.env.example` to `.env`
- Add your Stripe secret key (get it from your Stripe dashboard)
- Add your OpenAI API key

3. Run the server:
```bash
python father_bot.py
```

## How It Works

- Users can purchase bundles of 5 answers for $10.00
- Payment is processed securely through Stripe
- After successful payment, users receive credits for answers
- Each answer deducts one credit from the user's balance

## API Endpoints

1. Create Payment Intent:
```bash
POST /create-payment-intent
{
    "email": "user@example.com"
}
```

2. Process Successful Payment:
```bash
POST /payment-success
{
    "email": "user@example.com"
}
```

3. Get Answer:
```bash
POST /get-answer
{
    "email": "user@example.com",
    "question": "What advice do you have about..."
}
```

## Security Notes

- Never commit your `.env` file
- Keep your API keys secure
- Use HTTPS in production 