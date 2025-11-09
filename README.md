# Smart Feedback Collection and Analysis System

A full-stack web application that automatically analyzes user feedback sentiment using AI and provides real-time analytics for administrators.

## 🚀 Features

- **🤖 AI-Powered Sentiment Analysis** - Automatically classifies feedback as Positive, Negative, or Neutral using NLTK VADER and TextBlob
- **📊 Real-time Analytics Dashboard** - Interactive charts and visualizations with Chart.js
- **👥 User Management** - Secure registration and authentication with JWT
- **📧 Smart Notifications** - Automatic email alerts for critical negative feedback
- **💾 Data Export** - Export feedback data for further analysis
- **📱 Responsive Design** - Works seamlessly on desktop and mobile devices

## 🛠️ Tech Stack

### Frontend
- **HTML5** - Semantic structure and accessibility
- **CSS3** - Responsive design and modern styling
- **Vanilla JavaScript** - Client-side interactivity
- **Chart.js** - Data visualization and analytics

### Backend
- **Python 3.8+** - Core programming language
- **Flask** - Lightweight web framework
- **SQLAlchemy** - Database ORM and abstraction
- **JWT** - Secure authentication tokens

### AI/ML Components
- **NLTK VADER** - Primary sentiment analyzer
- **TextBlob** - Fallback sentiment analysis
- **Custom Rules** - Keyword-based final fallback

### Database
- **SQLite** - Relational database for development

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/sakethlingerker/Smart-Feedback-Collection-and-Analysis-System.git
   cd Smart-Feedback-Collection-and-Analysis-System
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
6. Access the application
   ```
   Open web browser and navigate to: http://localhost:5000
   ```


---
## 📈 Architecture & Workflow Overview

### *Workflow Steps*
1. *User Registration/Login* → Credentials verified & stored securely  
2. *Feedback Submission* → Data + optional image sent to backend  
3. *Sentiment Analysis* → Processed using VADER + TextBlob NLP  
4. *Database Storage* → Results stored in SQLite database  
5. *Admin Dashboard* → Data visualized using Chart.js  
6. *Report Generation* → Export as CSV or PDF

---
## 🏗️ Project Structure
      Smart-Feedback-System/
      ├── app.py                    # Main Flask application
      ├── models.py                 # Database models and schema
      ├── sentiment_analysis.py     # Sentiment analysis engine
      ├── auth_middleware.py        # Authentication middleware
      ├── email_notifier.py         # Email notification system
      ├── requirements.txt          # Python dependencies
      ├── init_db.py               # Database initialization script
      ├── templates/               # HTML templates
      │   ├── index.html           # Homepage and feedback form
      │   ├── login.html           # User login page
      │   ├── register.html        # User registration page
      │   ├── dashboard.html       # Admin analytics dashboard
      │   └── profile.html         # User profile and feedback history
      └── static/                  # Static assets
          ├── css/
          │   ├── main.css         # Main stylesheet
          │   └── dashboard.css    # Dashboard-specific styles
          ├── js/
          │   ├── main.js          # Frontend functionality
          │   ├── auth.js          # Authentication handling
          │   └── dashboard.js     # Dashboard charts and analytics
          └── images/              # Image assets
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

## 🏗 System Architecture

*(<img width="1648" height="567" alt="image" src="https://github.com/user-attachments/assets/e9a22223-f434-48db-a8e1-5af4f4f1301f" />
)*

---


---

## Contributing

1. Fork the repo
2. Create a feature branch
3. Open a PR with a clear description and tests

---

