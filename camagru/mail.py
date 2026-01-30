from flask import current_app, render_template
from flask_mail import Mail, Message
from threading import Thread

def send_email(message):
    app = current_app._get_current_object()
    Thread(target=send_email_async, args=(app, message)).start()

def send_email_async(app, msg):
    with app.app_context():
        mail = Mail(app)
        try:
            mail.send(msg)
            app.logger.info(f"Email sent to {msg.recipients}")
        except Exception as a:
            app.logger.error(f"Failed to send email to {msg.recipients}")

def registration_mail(username, email, token):
    subject = f"Welcome to Camagru {username}"
    recipients = [email]
    sender = "camagru@noreply.fr"
    html = render_template(
            "mail/registration.html",
            username = username,
            url = current_app.config["BASE_URL"] + f"/auth/verify/{token}"
        )
    send_email(Message(subject=subject, recipients=recipients, sender=sender, html=html))

def recovery_mail(username, email, token):
    subject = f"Camagru password reset"
    recipients = [email]
    sender = "camagru@noreply.fr"
    html = render_template(
            "mail/recovery.html",
            username = username,
            url = current_app.config["BASE_URL"] + f"/auth/reset/{token}"
        )
    send_email(Message(subject=subject, recipients=recipients, sender=sender, html=html))

def comment_mail(username, commenter, email, post_id):
    subject = f"New comment on your post"
    recipients = [email]
    sender = "camagru@noreply.fr"
    html = render_template(
            "mail/comment.html",
            username = username,
            commenter = commenter,
            url = current_app.config["BASE_URL"] + f"/browse/comment/{post_id}"
        )
    send_email(Message(subject=subject, recipients=recipients, sender=sender, html=html))