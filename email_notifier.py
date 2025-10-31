from flask_mail import Mail, Message
from flask import current_app
import logging


logger = logging.getLogger(__name__)

mail = Mail()

class EmailNotifier:
    def __init__(self):
        self.mail = mail
    
    def send_negative_feedback_alert(self, feedback):
        """Send email notification for negative feedback"""
        try:
            logger.info("📧 Preparing email notification...")
            
            # Check if email is configured
            if not current_app.config.get('MAIL_USERNAME') or not current_app.config.get('MAIL_PASSWORD'):
                logger.warning("⚠️ Email not configured. Skipping notification.")
                return False
                
            if not current_app.config.get('ADMIN_EMAIL'):
                logger.error("❌ Admin email not configured. Cannot send notification.")
                return False
                
            subject = f"🚨 Negative Feedback Alert - Sentiment: {feedback.sentiment}"
            
            # Create email body
            body = f"""
            Negative feedback has been submitted and requires attention.
            
            Feedback Details:
            - ID: {feedback.id}
            - Name: {feedback.name or 'Anonymous'}
            - Email: {feedback.email or 'Not provided'}
            - Category: {feedback.category}
            - Rating: {feedback.rating}/5
            - Sentiment: {feedback.sentiment} (Polarity: {feedback.polarity:.3f})
            - Analysis Method: {feedback.analysis_method}
            - Submitted: {feedback.created_at.strftime('%Y-%m-%d %H:%M:%S')}
            
            Feedback Message:
            "{feedback.message}"
            
            Please review this feedback and take appropriate action.
            
            Best regards,
            Smart Feedback System
            """
            
            html_body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #dc3545; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background: #f8f9fa; padding: 20px; border-radius: 0 0 8px 8px; }}
                    .detail-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                    .detail-table td {{ padding: 8px 12px; border-bottom: 1px solid #ddd; }}
                    .feedback-message {{ background: white; padding: 15px; border-left: 4px solid #dc3545; margin: 15px 0; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚨 Negative Feedback Alert</h1>
                    </div>
                    <div class="content">
                        <p>Negative feedback has been submitted and requires your attention.</p>
                        
                        <h3>Feedback Details:</h3>
                        <table class="detail-table">
                            <tr><td><strong>ID:</strong></td><td>{feedback.id}</td></tr>
                            <tr><td><strong>Name:</strong></td><td>{feedback.name or 'Anonymous'}</td></tr>
                            <tr><td><strong>Email:</strong></td><td>{feedback.email or 'Not provided'}</td></tr>
                            <tr><td><strong>Category:</strong></td><td>{feedback.category}</td></tr>
                            <tr><td><strong>Rating:</strong></td><td>{feedback.rating}/5</td></tr>
                            <tr><td><strong>Sentiment:</strong></td><td>{feedback.sentiment} (Polarity: {feedback.polarity:.3f})</td></tr>
                            <tr><td><strong>Analysis Method:</strong></td><td>{feedback.analysis_method}</td></tr>
                            <tr><td><strong>Submitted:</strong></td><td>{feedback.created_at.strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
                        </table>
                        
                        <h3>Feedback Message:</h3>
                        <div class="feedback-message">
                            "{feedback.message}"
                        </div>
                        
                        <p>Please review this feedback and take appropriate action.</p>
                    </div>
                    <div class="footer">
                        <p>Best regards,<br><strong>Smart Feedback System</strong></p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg = Message(
                subject=subject,
                recipients=[current_app.config['ADMIN_EMAIL']],
                body=body,
                html=html_body
            )
            
            logger.info(f"✉️ Sending email to: {current_app.config['ADMIN_EMAIL']}")
            from smtplib import SMTP
            SMTP.debuglevel = 0  # 🧹 Disable SMTP debug output completely

            self.mail.send(msg)
            logger.info(f"✅ Negative feedback alert sent successfully for feedback ID: {feedback.id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email notification: {e}")
            return False
    

# Global notifier instance
email_notifier = EmailNotifier()

def init_email(app):
    """Initialize email extension"""
    try:
        mail.init_app(app)

        # 🧹 Disable Flask-Mail internal SMTP debug output (even if Flask debug mode is on)
        app.config['MAIL_DEBUG'] = False

        # Optional: ensure SMTP debug is off globally
        import smtplib
        smtplib.SMTP.debuglevel = 0

        app.logger.info("✅ Email service initialized successfully")
    except Exception as e:
        app.logger.error(f"❌ Failed to initialize email service: {e}")


def send_negative_feedback_alert(feedback):
    """Convenience function to send negative feedback alert"""
    return email_notifier.send_negative_feedback_alert(feedback)