# modules/emails.py - Email Skill (IMAP/SMTP)
import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from config import EMAIL_USER, EMAIL_PASS, EMAIL_IMAP_SERVER, EMAIL_SMTP_SERVER

def check_emails(limit=5):
    """Check for recent unread emails."""
    try:
        # Connect to IMAP
        mail = imaplib.IMAP4_SSL(EMAIL_IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")
        
        # Search for unread emails
        status, messages = mail.search(None, 'UNSEEN')
        if status != 'OK':
            return "❌ Error searching emails."
            
        email_ids = messages[0].split()
        if not email_ids:
            return "📬 You have no unread emails, Ravi."
            
        results = []
        # Get latest emails
        for i in email_ids[-limit:]:
            res, msg_data = mail.fetch(i, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = msg["subject"]
                    sender = msg["from"]
                    results.append(f"📧 *{subject}*\nFrom: {sender}")
                    
        return "\n\n".join(results)
    except Exception as e:
        return f"❌ Email error: {e}"

def send_email(to, subject, body):
    """Send an email."""
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_USER
        msg['To'] = to
        
        with smtplib.SMTP_SSL(EMAIL_SMTP_SERVER, 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, [to], msg.as_string())
            
        return f"✅ Email sent to {to} successfully!"
    except Exception as e:
        return f"❌ Failed to send email: {e}"
