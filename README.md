
# AI Study Buddy

An intelligent flashcard generation application that converts your study notes into interactive flashcards using AI, with integrated payment processing via Chapa.co. The app now includes daily flashcard limits for basic users, email verification, profile management, user-specific dashboards, and improved notifications.


## Features (2025)

- 📝 **Smart Note Processing**: Paste your study notes and automatically generate flashcards
- 🤖 **AI-Powered Questions**: Intelligent question generation from your content
- 💾 **Database Storage**: Save flashcards to Supabase for later review
- 💳 **Payment Integration**: Secure payment processing with Chapa.co
- 🎨 **Modern UI**: Beautiful, responsive interface
- 📱 **Mobile Friendly**: Works on all devices
- 🔒 **User Authentication**: Signup, login, logout, and session management
- ✉️ **Email Verification**: Required for new users, with custom verification email
- 👤 **Profile Management**: Update profile picture, change password, remove account via modal
- 🛡️ **User-Specific Dashboard**: Each user sees only their own flashcards
- 🚦 **Daily Flashcard Limit**: Basic plan users can generate up to 10 flashcards per day; upgrade prompt shown in popup when limit reached
- 🔔 **Notifications**: Success, error, and info notifications for all major actions
- 💬 **Contact Support**: Modal contact form for support messages

## Setup Instructions

### 1. Prerequisites

- Python 3.7 or higher
- Supabase account
- Chapa.co account for payment processing
- Hugging Face API key (optional, for enhanced AI features)


### 2. Installation

1. Clone the repository:
```bash
git clone https://github.com/Cherg906/Hackathon-vibecode432.git
cd ai_study_buddy_supabase
```

2. Create a virtual environment:
```bash
rightpython -m venv venv
```

3. Activate the virtual environment:
```bash
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the root directory with the following variables:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# Chapa Payment Configuration
CHAPA_SECRET_KEY=your_chapa_secret_key
CHAPA_WEBHOOK_SECRET=your_chapa_webhook_secret

# Flask Configuration
FLASK_SECRET_KEY=your_flask_secret_key

# Hugging Face API Configuration (optional)
HUGGINGFACE_API_KEY=your_huggingface_api_key
HUGGINGFACE_MODEL=distilbert-base-uncased-distilled-squad
```


### 4. Database Setup
Includes tables for users, flashcards, and payments. Users table now supports avatar, password, and verification status.

1. Create a new Supabase project at [supabase.com](https://supabase.com)
2. Run the SQL schema in your Supabase SQL editor:

```sql
-- Copy and paste the contents of database_schema.sql
```

Or manually create the required tables:

```sql
-- Flashcards table
CREATE TABLE flashcards (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Payments table
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    tx_ref VARCHAR(255) UNIQUE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    email VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    plan_type VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    subscription_status VARCHAR(50) DEFAULT 'free',
    subscription_plan VARCHAR(50),
    subscription_expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 5. Chapa Payment Setup

1. **Create a Chapa Account**:
   - Sign up at [chapa.co](https://chapa.co)
   - Complete your account verification

2. **Get Your API Keys**:
   - Go to your Chapa dashboard
   - Navigate to API Keys section
   - Copy your Secret Key and Webhook Secret

3. **Configure Webhooks** (Optional but Recommended):
   - In your Chapa dashboard, set up webhooks
   - Webhook URL: `https://yourdomain.com/payment-webhook`
   - For local development, use ngrok: `ngrok http 5000`

4. **Test Mode**:
   - Use Chapa's test mode for development
   - Test cards are available in the Chapa documentation


### 6. Running the Application
App enforces daily flashcard limit for basic users. If limit is reached, a popup notification appears with upgrade link and close (×) button.

1. Start the Flask application:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage


### Basic Features
- Email verification required for signup
- Profile update modal: change password, upload avatar, remove account
- Daily flashcard limit for basic users
- Upgrade prompt and payment integration for premium plan

1. **Generate Flashcards**:
   - Paste your study notes into the text area
   - Click "Generate Flashcards"
   - View your automatically generated flashcards

2. **View All Flashcards**:
   - Click "View All Flashcards" to see all saved flashcards
   - Flashcards are stored in your Supabase database


### Payment Features
- Chapa payment integration for plan upgrades
- Payment success/failure pages

1. **Upgrade to Premium**:
   - Click "Upgrade Plan" to access premium features
   - Choose from Basic (Free), Premium ($9.99/month), or Pro ($19.99/month)
   - Complete payment through Chapa's secure checkout

2. **Payment Processing**:
   - Payments are processed securely through Chapa
   - Multiple payment methods supported (cards, mobile money, bank transfers)
   - Automatic webhook handling for payment status updates

3. **Subscription Management**:
   - Payment history stored in database
   - Automatic subscription status updates
   - Support for multiple currencies


## API Endpoints
- `/api/login` - Login endpoint
- `/api/signup` - Signup endpoint (with email verification)
- `/api/update_profile` - Update profile (avatar, password)
- `/api/remove_account` - Remove user account

### Core Endpoints
- `GET /` - Main application page
- `POST /generate` - Generate flashcards from notes
- `GET /dashboard` - View all saved flashcards

### Payment Endpoints
- `GET /payment` - Payment page with pricing plans
- `POST /create-payment` - Create a new payment transaction
- `POST /payment-webhook` - Handle payment webhooks from Chapa
- `GET /verify-payment/<tx_ref>` - Verify a payment transaction
- `GET /payment-success` - Payment success page
- `GET /payment-failed` - Payment failed page


## Project Structure
Includes static JS for notifications and popup modals, and templates for all major pages and modals.

```
ai_study_buddy_supabase/
├── app.py                 # Main Flask application
├── supabase_client.py     # Supabase client configuration
├── requirements.txt       # Python dependencies
├── database_schema.sql    # Database schema
├── .env                   # Environment variables (create this)
├── static/
│   ├── app.js            # Frontend JavaScript
│   └── style.css         # CSS styles
├── templates/
│   ├── index.html        # Main page template
│   ├── dashboard.html    # Dashboard template
│   ├── payment.html      # Payment page template
│   ├── payment_success.html # Payment success page
│   └── payment_failed.html  # Payment failed page
└── payments/
    └── chapa.py          # Chapa payment integration
```

## Payment Integration Details

### Supported Payment Methods
- Credit/Debit Cards (Visa, Mastercard, etc.)
- Mobile Money (M-Pesa, MTN Mobile Money, etc.)
- Bank Transfers
- Digital Wallets

### Supported Currencies
- USD (US Dollar)
- EUR (Euro)
- ETB (Ethiopian Birr)
- NGN (Nigerian Naira)
- KES (Kenyan Shilling)
- And many more...

### Security Features
- Webhook signature verification
- Secure API key handling
- Payment status verification
- Database transaction logging


## Testing
Test daily flashcard limit and upgrade popup by generating more than 10 flashcards in one day as a basic user.

### Test the Application
```bash
python app.py
```

### Test Payment Integration
1. Use Chapa's test mode
2. Use test card numbers provided by Chapa
3. Verify webhook handling with ngrok

### Test Cards (Development Only)
- Card Number: 4242424242424242
- Expiry: Any future date
- CVV: Any 3 digits

## Troubleshooting

### Common Issues

1. **"No notes provided" error**:
   - Make sure you're entering text in the textarea
   - Check that the form is being submitted correctly

2. **Supabase connection errors**:
   - Verify your Supabase URL and key in the `.env` file
   - Ensure the required tables exist in your database

3. **Payment initialization errors**:
   - Check your Chapa API keys
   - Verify webhook URL configuration
   - Ensure proper currency codes

4. **Webhook errors**:
   - Check webhook signature verification
   - Verify webhook URL is accessible
   - Check database connection for payment storage

### Debug Mode

To run the application in debug mode for development:

```bash
export FLASK_ENV=development
python app.py
```

## Security Considerations

1. **Environment Variables**: Never commit your `.env` file to version control
2. **API Keys**: Keep your Chapa and Supabase keys secure
3. **Webhooks**: Use HTTPS in production for webhook URLs
4. **Database**: Regularly backup your Supabase database
5. **Payments**: Always verify payment status before providing access

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions:
- Check the troubleshooting section
- Review Chapa documentation at [docs.chapa.co](https://docs.chapa.co)
- Open an issue on the repository


## Changelog
### v1.1.0 (August 2025)
- Added daily flashcard limit for basic users
- Popup notification for upgrade with link and close button
- Email verification on signup
- Profile update modal (avatar, password, account removal)
- User-specific dashboard filtering

### v1.0.0
- Initial release with basic flashcard generation
- Supabase integration for data storage
- Chapa payment integration
- Modern responsive UI
- Webhook handling for payment status
