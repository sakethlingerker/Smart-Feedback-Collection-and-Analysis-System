import smtplib, os
from dotenv import load_dotenv

load_dotenv()

try:
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
        server.starttls()
        server.login(os.getenv("MAIL_USERNAME"), os.getenv("MAIL_PASSWORD"))
        server.sendmail(
            os.getenv("MAIL_USERNAME"),
            os.getenv("ADMIN_EMAIL"),
            "Subject: SMTP Test\n\nHello, this is a test email!"
        )
    print("✅ Email sent manually!")
except Exception as e:
    print(f"❌ Error: {e}")
