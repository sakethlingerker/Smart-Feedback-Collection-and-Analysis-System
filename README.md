# Smart Feedback Collection and Analysis System

![Version](https://img.shields.io/badge/Version-1.0.0-brightgreen) ![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![Flask](https://img.shields.io/badge/Flask-2.3.3-lightgrey)

A full‑stack web application to collect user feedback, run instant sentiment analysis, store results, and provide an administrator dashboard with visual analytics and export features.

---

## Quick summary

- Guests can submit anonymous feedback.
- Registered users can submit feedback, view and manage their history.
- Administrators access a dashboard with sentiment distribution, word clouds, priority matrix, exports, and email alerts for negative feedback.
- Sentiment analysis uses TextBlob and NLTK VADER with fallback rules.

---

## Features

- Real‑time sentiment analysis (TextBlob, VADER)
- Role‑based access: Guest, Registered User, Admin
- Dashboard: charts, trends, word clouds, live refresh
- Data export: CSV / JSON
- Email notifications for critical/negative feedback
- SQLite by default (configurable to other RDBMS)
- JWT authentication for APIs

---

## Tech stack

- Backend: Flask 2.3.3, Flask‑SQLAlchemy, Flask‑Mail
- NLP: TextBlob, NLTK (VADER)
- Frontend: HTML5, CSS3, JavaScript (ES6+), Chart.js
- DB: SQLite (default)
- Auth: JWT

---

## Quick start (Windows)

1. Clone and enter repo
   ```
   git clone https://github.com/sakethlingerker/Smart-Feedback-Collection-and-Analysis-System.git
   cd "Smart Feedback Collection and Analysis System"
   ```
2. Create and activate venv
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies
   ```
   pip install -r requirements.txt
   ```
4. Initialize database and create default admin
   ```
   python init_db.py
   ```
5. Run the app
   ```
   python app.py
   ```
6. Open in browser: http://localhost:5000

Default admin:
- Email: admin@feedback.com
- Password: admin123

---

## Usage overview

- Guest feedback form: name (optional), email (optional), category, rating (1–5), message (min 10 chars) → analyzed and stored.
- Registered users: register → login → feedback linked to account → view/delete own feedback.
- Admins: login → dashboard → view all feedback, filter, export, receive alerts.

---

## API (examples)

- POST /api/auth/register — register user
- POST /api/auth/login — obtain JWT
- GET /api/auth/me — current user
- POST /api/feedback — submit feedback
- GET /api/user/feedback — user feedbacks
- GET /api/feedback — all feedbacks (admin)
- GET /api/analytics — dashboard metrics
- GET /api/wordcloud — word cloud data
- GET /api/export/csv, /api/export/json — data export

(Refer to backend routes for full request/response schemas.)

---

## Project structure (high level)

- backend/ — Flask app, models, routes, NLP, mail helpers
- frontend/ — HTML, CSS, JS, dashboard scripts
- init_db.py — DB initialization and seed data
- requirements.txt — Python deps
- README.md — this file

---

## Development notes

- Switch DB by updating DATABASE_URL in config or .env.
- For production, serve via WSGI (Gunicorn) and configure environment variables for secret keys and mail.
- Ensure NLTK VADER data is available (nltk.download('vader_lexicon')) when setting up.

---

## Testing

- Add/execute unit tests for:
  - Auth endpoints (JWT lifecycle)
  - Feedback submit and storage
  - Sentiment analysis output
  - Export endpoints
- Use the provided test design template for manual and automated cases.

---

## Contributing

1. Fork the repo
2. Create a feature branch
3. Open a PR with a clear description and tests

---

