
# AI Study Buddy App – Feature & Prompt Documentation

This document summarizes the current features, user flows, and prompts for the AI Study Buddy web app as of August 2025. Use it to guide further development, onboarding, and feature requests.

---

## Current Features & Status

### 1. Authentication & User Management
- Secure signup, login, and logout with Supabase backend
- Email verification required for new users (customized verification email)
- Session-based dashboard filtering (each user sees only their own flashcards)
- Profile update modal: change password, upload avatar, remove account
- Avatar and user name displayed in header; avatar opens profile modal

### 2. Flashcard Generation & Limits
- AI-powered flashcard generation from study notes (Hugging Face API)
- Daily limit: Basic plan users can generate up to 10 flashcards per day
- If limit reached, popup notification appears: "You have reached the daily limit of generating flashcards. Please come back tomorrow or upgrade your plan." Includes upgrade link and close (×) button
- Premium plan available via Chapa payment integration

### 3. Dashboard & Data
- Dashboard page shows user’s flashcards grouped by session
- Pagination and statistics for flashcard sessions
- Only logged-in users can access their dashboard

### 4. UI/UX & Notifications
- Modern, responsive design for desktop and mobile
- Modal forms for login/signup, profile update, and contact support
- Success/error/info notifications for all major actions
- Contact modal for support messages (via SMTP)
- Favicon, background image, and branding

### 5. Backend & API
- RESTful endpoints for login, signup, profile update, account removal, flashcard generation, and support messages
- Error handling and logging for all endpoints
- Secure user data and session management
- Add a `/generate` endpoint to create flashcards from notes.
- Add a `/send_message` endpoint to send support emails via SMTP.
- Add error handling and logging for all endpoints.
- Secure API endpoints and user data.

### 6. Payment & Upgrades
- Chapa payment integration for plan upgrades
- Payment success/failure pages

### 7. Deployment & Testing
- requirements.txt and .env for easy setup
- Instructions for local and production deployment

## 8. Advanced Features
- Allow users to upload profile pictures during signup.
- Add pagination and statistics to the dashboard.
- Add payment success/failure pages.


