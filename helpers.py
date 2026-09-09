import json
from werkzeug.security import check_password_hash
from settings import PASSWORD_PATH


def has_password_file():
    return PASSWORD_PATH.exists()


def check_password(password):
    if not has_password_file():
        return False
    with PASSWORD_PATH.open(encoding="utf-8") as stream:
        data = json.load(stream)
    return check_password_hash(data["password"], password)
