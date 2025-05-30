import os
import json
import secrets
import string
from werkzeug.security import generate_password_hash, check_password_hash

KEY_FILE = "key.json"

def has_password_file():
    return os.path.exists(KEY_FILE)

def generate_strong_password(length=16):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_password_file():
    plain = generate_strong_password()
    hashed = generate_password_hash(plain)
    with open(KEY_FILE, "w") as f:
        json.dump({"password": hashed}, f)
    return plain  # returnera plaintext så det kan visas en gång

def check_password(password):
    if not has_password_file():
        return False
    with open(KEY_FILE) as f:
        data = json.load(f)
    return check_password_hash(data["password"], password)
