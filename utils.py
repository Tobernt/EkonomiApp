from flask import session, redirect, url_for
from functools import wraps

def require_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("start"))
        return func(*args, **kwargs)
    return wrapper
