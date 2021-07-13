import os.path
import re

from PyQt5.QtWidgets import QMessageBox


def get_api_key():
    path = os.path.dirname(__file__) + '/../key.txt'
    with open(path, "r") as f:
        key = f.read()
    if key is None or ' ' in key:
        showdialog("Api key not valid", "Check key.txt file", f"Api key:\n'{key}'\nIs not valid...")
        return None
    return key


def title_to_underscore_title(title: str):  # Treure els espais i caràcters especials del títol
    title = re.sub('[\W_]+', "_", title)
    return title.lower()


def id_to_url(v_id: str):  # Passar la ID del video a URL
    v_url = "https://youtu.be/" + v_id
    return v_url


def url_to_id(url: str):  # Passar la URL de la playlist a ID
    return url.rsplit("=", 1)[1]


def percent(tem, total):
    perc = (float(tem) / float(total)) * float(100)
    return perc


def showdialog(message, aditional_text="", extra_details=""):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)

    msg.setText(f"{message}")
    msg.setInformativeText(f"{aditional_text}")
    msg.setWindowTitle("Warning")
    msg.setDetailedText(f"{extra_details}")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.buttonClicked.connect(msgbtn)

    retval = msg.exec_()
    print(f"value of pressed message box button: {retval}")


def msgbtn(i):
    print(f"Button pressed is: {i.text()}")
