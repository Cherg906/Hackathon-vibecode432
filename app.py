# ...existing code...
# ...existing code...
# ...existing code...
from flask import Flask, render_template, request, jsonify, url_for
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your-secret-key-here")

# Supabase client setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in the .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
serializer = URLSafeTimedSerializer(app.secret_key)

# Update profile route
@app.route("/api/update_profile", methods=["POST"])
def update_profile():
    from flask import session
    data = request.get_json()
    email = session.get("user_email")
    if not email:
        return jsonify({"status": "error", "message": "Not logged in."}), 401
    avatar = data.get("avatar")
    new_password = data.get("new_password")
    updates = {}
    if avatar:
        updates["avatar"] = avatar
    if new_password:
        updates["password"] = generate_password_hash(new_password)
    if not updates:
        return jsonify({"status": "error", "message": "No changes provided."}), 400
    try:
        supabase.table("users").update(updates).eq("email", email).execute()
        return jsonify({"status": "ok", "message": "Profile updated successfully."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def send_verification_email(email, token):

    verify_url = url_for('verify_email', token=token, _external=True)
    subject = "Verify Your Email"
    body = f"""
<html>
<body>
<p>Dear User,</p>
<p>Please verify your email which is used for signing up at the AI Study Buddy.</p>
<p>
<a href='{verify_url}' style='display:inline-block;padding:10px 20px;background:#2563eb;color:#fff;text-decoration:none;border-radius:6px;'>Verify Email</a>
</p>
<p>Or copy and paste this link into your browser:<br>
<span style='color:#2563eb'>{verify_url}</span>
</p>
<p>With Regards,<br>the developer</p>
</body>
</html>
"""
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    to_email = email
    msg = MIMEMultipart('alternative')
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        print("Verification email send error:", e)
# Email verification route
@app.route('/verify-email/<token>')
def verify_email(token):
    try:
        email = serializer.loads(token, max_age=3600)
    except Exception:
        return "Invalid or expired token.", 400
    result = supabase.table("users").select("*").eq("email", email).execute()
    if not result.data:
        return "User not found.", 404
    user = result.data[0]
    supabase.table("users").update({"verified": True}).eq("email", email).execute()
    return '''
    <html>
    <body>
        <h2>Email verified! You can now log in.</h2>
        <a href="/">Go to Login</a>
    </body>
    </html>
    ''', 200
    verify_url = url_for('verify_email', token=token, _external=True)
    subject = "Verify Your Email"
    body = f"""
<html>
<body>
<p>Dear User,</p>
<p>Please verify your email which is used for signing up at the AI Study Buddy.</p>
<p>
<a href='{verify_url}' style='display:inline-block;padding:10px 20px;background:#2563eb;color:#fff;text-decoration:none;border-radius:6px;'>Verify Email</a>
</p>
<p>Or copy and paste this link into your browser:<br>
<span style='color:#2563eb'>{verify_url}</span>
</p>
<p>With Regards,<br>the developer</p>
</body>
</html>
"""
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    to_email = email
    msg = MIMEMultipart('alternative')
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        print("Verification email send error:", e)
@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    avatar = data.get("avatar")
    if not name or not email or not password:
        return jsonify({"status": "error", "message": "All fields are required."}), 400
    result = supabase.table("users").select("*").eq("email", email).execute()
    if result.data:
        return jsonify({"status": "error", "message": "Email already registered."}), 409
    hashed_password = generate_password_hash(password)
    user_data = {"name": name, "email": email, "password": hashed_password, "avatar": avatar, "verified": False}
    try:
        res = supabase.table("users").insert(user_data).execute()
        user = res.data[0] if res.data else user_data
        user_info = {k: v for k, v in user.items() if k != "password"}
        # Send verification email
        token = serializer.dumps(email)
        send_verification_email(email, token)
        return jsonify({"status": "ok", "user": user_info, "message": "Verification email sent. Please check your inbox."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"status": "error", "message": "Email and password required."}), 400
    result = supabase.table("users").select("*").eq("email", email).execute()
    users = result.data
    if not users:
        return jsonify({"status": "error", "message": "No account found for this email."}), 401
    user = users[0]
    if not user.get("verified"):
        return jsonify({"status": "error", "message": "Email not verified. Please check your inbox."}), 403
    if not check_password_hash(user.get("password"), password):
        return jsonify({"status": "error", "message": "Incorrect password."}), 401
    user_info = {k: v for k, v in user.items() if k != "password"}
    # Store user email in session for dashboard security
    from flask import session
    session["user_email"] = user_info["email"]
    return jsonify({"status": "ok", "user": user_info})
from flask import Flask, render_template, request, jsonify, url_for
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# ...existing code...

# Hugging Face API setup
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "distilbert-base-uncased-distilled-squad")
HF_API_URL = f"https://api-inference.huggingface.co/models/{HUGGINGFACE_MODEL}"
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

# Initialize Chapa payment
try:
    from payments.chapa import ChapaPayment
    chapa = ChapaPayment()
except Exception as e:
    print(f"Warning: Chapa payment not initialized: {e}")
    chapa = None

# Contact form endpoint
@app.route("/send_message", methods=["POST"])
def send_message():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    message = data.get("message")
    if not name or not email or not message:
        return jsonify({"status": "error", "message": "All fields are required."}), 400

    # Email settings
    to_email = "chernetg@gmail.com"
    subject = f"AI Study Buddy Support Message from {name}"
    body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

    # SMTP config (use environment variables for security)
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")  # Your Gmail address
    smtp_password = os.getenv("SMTP_PASSWORD")  # App password or Gmail password

    if not smtp_user or not smtp_password:
        return jsonify({"status": "error", "message": "Email service not configured."}), 500

    try:
        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
        return jsonify({"status": "ok"})
    except Exception as e:
        print("Email send error:", e)
        return jsonify({"status": "error", "message": "Failed to send email."}), 500

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)  # Default 10 sessions per page
        
        # Ensure valid page numbers
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 50:  # Limit per_page to reasonable range
            per_page = 10
        
        # Get user email from query parameter or session (for demo, use query param)
        from flask import session
        user_email = session.get("user_email")
        if not user_email:
            return "You must be logged in to view your dashboard.", 401
        # Fetch only flashcards for this user
        result = supabase.table("flashcards").select("*").eq("email", user_email).order("created_at", desc=True).execute()
        flashcards = result.data
        
        # Process flashcards to ensure proper timestamp handling
        from datetime import datetime, timedelta, timezone
        eat_tz = timezone(timedelta(hours=3))  # East African Time UTC+3
        for flashcard in flashcards:
            if flashcard.get('created_at'):
                # Convert string timestamp to datetime if needed
                if isinstance(flashcard['created_at'], str):
                    try:
                        dt = datetime.fromisoformat(flashcard['created_at'].replace('Z', '+00:00'))
                        flashcard['created_at'] = dt.astimezone(eat_tz)
                    except:
                        flashcard['created_at'] = None
                elif isinstance(flashcard['created_at'], datetime):
                    flashcard['created_at'] = flashcard['created_at'].astimezone(eat_tz)
            else:
                flashcard['created_at'] = None
        
        # Group flashcards by session (same timestamp = same session)
        from collections import defaultdict
        sessions = defaultdict(list)
        
        for flashcard in flashcards:
            if flashcard['created_at']:
                # Round to nearest minute to group very close timestamps
                from datetime import timedelta
                rounded_time = flashcard['created_at'].replace(second=0, microsecond=0)
                sessions[rounded_time].append(flashcard)
            else:
                # Group flashcards without timestamps together
                sessions[None].append(flashcard)
        
        # Convert to list of tuples and sort by timestamp (newest first)
        session_list = sorted(sessions.items(), key=lambda x: x[0] if x[0] else datetime.min, reverse=True)
        
        # Calculate pagination
        total_sessions = len(session_list)
        total_pages = (total_sessions + per_page - 1) // per_page  # Ceiling division
        
        # Ensure page is within valid range
        if page > total_pages and total_pages > 0:
            page = total_pages
        
        # Get sessions for current page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        current_page_sessions = session_list[start_idx:end_idx]
        
        # Calculate total flashcards across all sessions (for statistics)
        total_flashcards = sum(len(session_flashcards) for _, session_flashcards in session_list)
        sessions_with_timestamps = sum(1 for timestamp, _ in session_list if timestamp is not None)
        
        # Pagination info
        pagination_info = {
            'current_page': page,
            'total_pages': total_pages,
            'per_page': per_page,
            'total_sessions': total_sessions,
            'total_flashcards': total_flashcards,
            'sessions_with_timestamps': sessions_with_timestamps,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_page': page - 1 if page > 1 else None,
            'next_page': page + 1 if page < total_pages else None
        }
                
    except Exception as e:
        current_page_sessions = []
        pagination_info = {
            'current_page': 1,
            'total_pages': 1,
            'per_page': per_page,
            'total_sessions': 0,
            'total_flashcards': 0,
            'sessions_with_timestamps': 0,
            'has_prev': False,
            'has_next': False,
            'prev_page': None,
            'next_page': None
        }
        print("Supabase fetch error:", e)
    
    return render_template("dashboard.html", 
                         sessions=current_page_sessions, 
                         pagination=pagination_info)

@app.route("/payment")
def payment():
    return render_template("payment.html")

@app.route("/create-payment", methods=["POST"])
def create_payment():
    """Create a new payment transaction"""
    if not chapa:
        return jsonify({"status": "error", "message": "Payment service not available"}), 503
    
    try:
        data = request.get_json()
        amount = data.get("amount")
        currency = data.get("currency", "USD")
        email = data.get("email")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        
        if not amount or not email:
            return jsonify({"status": "error", "message": "Amount and email are required"}), 400
        
        # Create payment
        result = chapa.create_payment(
            amount=float(amount),
            currency=currency,
            email=email,
            first_name=first_name,
            last_name=last_name,
            callback_url=url_for("payment_webhook", _external=True),
            return_url=url_for("payment_success", _external=True),
            customizations={
                "title": "AI Study Buddy Premium",
                "description": "Upgrade to premium features"
            }
        )
        
        if result["status"] == "success":
            # Store payment info in session or database
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/payment-webhook", methods=["POST"])
def payment_webhook():
    """Handle payment webhooks from Chapa"""
    if not chapa:
        return jsonify({"status": "error", "message": "Payment service not available"}), 503
    
    try:
        # Get webhook signature
        signature = request.headers.get("Chapa-Signature")
        if not signature:
            return jsonify({"status": "error", "message": "Missing signature"}), 400
        
        # Process webhook
        payload = request.get_json()
        result = chapa.process_webhook(payload, signature)
        
        # Update database based on payment status
        if result["action"] == "payment_success":
            # Update user subscription in database
            tx_ref = result["tx_ref"]
            try:
                # You can store successful payments in your database
                supabase.table("payments").insert({
                    "tx_ref": tx_ref,
                    "status": "success",
                    "amount": result["amount"],
                    "currency": result["currency"],
                    "email": payload.get("email")
                }).execute()
            except Exception as e:
                print(f"Failed to store payment: {e}")
        
        return jsonify({"status": "success"})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/verify-payment/<tx_ref>")
def verify_payment(tx_ref):
    """Verify a payment transaction"""
    if not chapa:
        return jsonify({"status": "error", "message": "Payment service not available"}), 503
    
    try:
        result = chapa.verify_payment(tx_ref)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/payment-success")
def payment_success():
    """Payment success page"""
    tx_ref = request.args.get("tx_ref")
    return render_template("payment_success.html", tx_ref=tx_ref)

@app.route("/payment-failed")
def payment_failed():
    """Payment failed page"""
    return render_template("payment_failed.html")

@app.route("/generate", methods=["POST"])
def generate():
    # Handle both form data and JSON requests
    notes = None
    # Check for form data first
    if request.form:
        notes = request.form.get("notes") or request.form.get("text")
    # Check for JSON data
    if not notes and request.is_json:
        json_data = request.get_json()
        notes = json_data.get("notes") or json_data.get("text")
    if not notes:
        return jsonify({"status": "error", "message": "No notes or text provided"}), 400

    # Enforce daily flashcard limit for basic plan
    from flask import session
    user_email = session.get("user_email")
    if not user_email:
        return jsonify({"status": "error", "message": "Not logged in."}), 401

    from datetime import datetime, timedelta
    import pytz
    # Use UTC for consistency
    now = datetime.utcnow()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Query flashcards created today by this user
    result = supabase.table("flashcards").select("created_at").eq("email", user_email).gte("created_at", start_of_day.isoformat()).lte("created_at", end_of_day.isoformat()).execute()
    flashcards_today = len(result.data) if result.data else 0
    DAILY_LIMIT = 10
    if flashcards_today >= DAILY_LIMIT:
        return jsonify({
            "status": "limit",
            "message": f"You have reached your daily limit of {DAILY_LIMIT} flashcards. Please upgrade your plan to continue generating more."
        }), 403

    # Create questions based on the input text
    try:
        text_sentences = [s.strip() for s in notes.split('.') if s.strip()]
        questions = []
        question_templates = [
            "What is the main concept about: {}?",
            "Explain the key point: {}",
            "What does this statement mean: {}?",
            "Summarize the following: {}",
            "What are the important details about: {}?"
        ]
        for i, sentence in enumerate(text_sentences[:5]):  # Limit to 5 questions
            if len(sentence) > 15:
                template = question_templates[i % len(question_templates)]
                question = template.format(sentence[:60] + "..." if len(sentence) > 60 else sentence)
                answer = sentence
                questions.append({"question": question, "answer": answer})
        if not questions:
            words = notes.split()
            if len(words) > 20:
                chunk_size = max(1, len(words) // 5)
                for i in range(5):
                    start = i * chunk_size
                    end = start + chunk_size if i < 4 else len(words)
                    chunk = " ".join(words[start:end])
                    if len(chunk) > 20:
                        question = f"What are the key points in this section: {chunk[:50]}..."
                        questions.append({"question": question, "answer": chunk})
            else:
                questions = [{
                    "question": "What are the key points from the provided notes?",
                    "answer": notes[:300] + "..." if len(notes) > 300 else notes
                }]
            questions = questions[:5]
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to generate questions: {e}"}), 500

    # Only insert up to the remaining daily limit
    remaining = DAILY_LIMIT - flashcards_today
    questions_to_insert = questions[:remaining]
    inserted = []
    for q in questions_to_insert:
        try:
            res = supabase.table("flashcards").insert({
                "question": q["question"],
                "answer": q["answer"],
                "email": user_email
            }).execute()
            if res.data:
                inserted.append(res.data[0])
        except Exception as e:
            print("Supabase insert error:", e)

    return jsonify({
        "status": "ok",
        "questions": questions_to_insert,
        "inserted": inserted,
        "remaining": DAILY_LIMIT - (flashcards_today + len(inserted)),
        "limit": DAILY_LIMIT
    })

if __name__ == "__main__":
    import os

    # Get the port assigned by Render, default to 5000 locally
    port = int(os.environ.get("PORT", 5000))
    
    # Bind to 0.0.0.0 so it is accessible externally
    app.run(host="0.0.0.0", port=port, debug=False)
