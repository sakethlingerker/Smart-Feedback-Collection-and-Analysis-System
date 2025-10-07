import os
from dotenv import load_dotenv
from flask import Flask
from flask_mail import Mail, Message

load_dotenv()

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

def test_email():
    with app.app_context():
        try:
            msg = Message(
                subject="Test Email from Feedback System",
                recipients=[os.getenv('ADMIN_EMAIL')],
                body="This is a test email from your Smart Feedback System!"
            )
            mail.send(msg)
            print("✅ Email sent successfully!")
            return True
        except Exception as e:
            print(f"❌ Email failed: {e}")
            return False

if __name__ == "__main__":
    test_email()