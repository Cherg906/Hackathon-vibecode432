# Chapa Payment Integration Setup Guide

## 🚨 Current Issue
Your application is showing "Payment service not available" because the Chapa environment variables are not configured.

## 🔧 Quick Fix

### Step 1: Create .env file
Create a file named `.env` in your project root directory with the following content:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# Chapa Payment Configuration (REQUIRED)
CHAPA_SECRET_KEY=your_chapa_secret_key_here
CHAPA_WEBHOOK_SECRET=your_chapa_webhook_secret_here

# Flask Configuration
FLASK_SECRET_KEY=your_flask_secret_key_here

# Hugging Face API Configuration (optional)
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
HUGGINGFACE_MODEL=distilbert-base-uncased-distilled-squad
```

### Step 2: Get Chapa API Keys

1. **Visit Chapa.co**: Go to [https://chapa.co](https://chapa.co)
2. **Sign up/Login**: Create an account or log in to your existing account
3. **Navigate to Dashboard**: Go to your Chapa dashboard
4. **API Keys Section**: Look for "API Keys" or "Developer" section
5. **Copy Keys**: Copy your Secret Key and Webhook Secret

### Step 3: Update .env file
Replace the placeholder values in your `.env` file with your actual Chapa API keys:

```env
CHAPA_SECRET_KEY=CHS_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CHAPA_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 4: Test the Integration

Run the test script to verify your setup:

```bash
python test_chapa.py
```

### Step 5: Start the Application

```bash
python app.py
```

Then visit: http://localhost:5000/payment

## 🧪 Testing Payments

### Test Mode
- Use Chapa's test mode for development
- Test card number: `4242424242424242`
- Any future expiry date
- Any 3-digit CVV

### Test the Payment Flow
1. Go to http://localhost:5000/payment
2. Select a plan (Premium or Pro)
3. Fill in your details
4. Use test card information
5. Complete the payment

## 🌐 Webhook Setup (Optional)

For production or advanced testing:

1. **Install ngrok**: `npm install -g ngrok`
2. **Start ngrok**: `ngrok http 5000`
3. **Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)
4. **Set webhook URL** in Chapa dashboard: `https://abc123.ngrok.io/payment-webhook`

## 🔍 Troubleshooting

### Common Issues

1. **"Payment service not available"**
   - Check that CHAPA_SECRET_KEY is set in .env file
   - Verify the API key is correct
   - Restart the application after updating .env

2. **"Invalid API key"**
   - Double-check your Chapa Secret Key
   - Make sure you're using the correct key (not the public key)
   - Verify your Chapa account is active

3. **"Network error"**
   - Check your internet connection
   - Verify Chapa.co is accessible
   - Check if Chapa services are down

### Debug Steps

1. **Check environment variables**:
   ```bash
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('CHAPA_SECRET_KEY:', 'SET' if os.getenv('CHAPA_SECRET_KEY') else 'MISSING')"
   ```

2. **Test Chapa connection**:
   ```bash
   python test_chapa.py
   ```

3. **Check application logs**:
   Look for error messages when starting the app

## 📞 Support

If you're still having issues:

1. **Check Chapa Documentation**: [https://developer.chapa.co](https://developer.chapa.co)
2. **Chapa Support**: Contact Chapa support through their dashboard
3. **Application Issues**: Check the application logs for specific error messages

## ✅ Success Indicators

When everything is working correctly, you should see:

1. ✅ No "Payment service not available" error
2. ✅ Payment form loads properly
3. ✅ Can select plans and fill payment details
4. ✅ Redirects to Chapa checkout page
5. ✅ Payment processing works with test cards

## 🎉 Next Steps

Once payments are working:

1. **Test with real cards** (in production mode)
2. **Set up webhooks** for payment status updates
3. **Configure subscription management**
4. **Deploy to production**

---

**Need Help?** Run `python test_chapa.py` for detailed diagnostics!
