from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
import database
import logic
import os
import json
from utils import require_auth
from werkzeug.utils import secure_filename
from datetime import datetime
from helpers import has_password_file, create_password_file, check_password

app = Flask(__name__)
app.secret_key = "superhemlig"
UPLOAD_FOLDER = "uploads"
LOCK_FILENAME = ".lock.json"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/start", methods=["GET", "POST"])
def start():
    if not has_password_file():
        flash("Ingen 'key.json' hittades. Lägg till ett lösenord med verktyget först.", "danger")
        return render_template("startup.html", generated=True)

    if request.method == "POST":
        password = request.form.get("password", "").strip()
        if check_password(password):
            session["authenticated"] = True
            flash("Inloggning lyckades!", "success")
            return redirect(url_for("index"))
        else:
            flash("Fel lösenord.", "danger")
            return redirect(url_for("start"))

    return render_template("startup.html", generated=False)

@app.route("/")
@require_auth
def index():
    valdmånad = request.args.get("månad")
    valdår = request.args.get("år")
    alla = database.get_info()

    år_lista = sorted(set([r[4][:4] for r in alla]))
    månads_lista = sorted(set([r[4][5:7] for r in alla]))

    transaktioner = alla
    if valdår:
        transaktioner = [r for r in transaktioner if r[4][:4] == valdår]
    if valdmånad:
        transaktioner = [r for r in transaktioner if r[4][5:7] == valdmånad]

    inkomst = sum(r[3] for r in transaktioner if r[6] == "Inkomst")
    utgift = sum(r[3] for r in transaktioner if r[6] == "Utgift")
    saldo = inkomst - utgift

    return render_template("index.html",
        transactions=transaktioner,
        valdmånad=valdmånad,
        valdår=valdår,
        månader=månads_lista,
        år=år_lista,
        inkomst=inkomst,
        utgift=utgift,
        saldo=saldo
    )

@app.route("/ny", methods=["GET", "POST"])
@require_auth
def add_transaction():
    if request.method == "POST":
        date = request.form["date"]
        category = request.form["category"]
        item_name = request.form["item_name"]
        description = request.form.get("description", "")
        amount = float(request.form["amount"])
        type_ = request.form["type"]
        taxrate = float(request.form.get("taxrate", 30)) / 100

        success, message = logic.add_transaction(date, category, item_name, amount, description, type_, taxrate)
        flash(message, "success" if success else "danger")
        return redirect(url_for("index"))

    return render_template("add_edit.html", transaction=None, current_date=datetime.today().date().isoformat(), categories=database.get_categories())

@app.route("/redigera/<int:id>", methods=["GET", "POST"])
@require_auth
def edit_transaction(id):
    transaction = database.get_info_by_id(id)
    if request.method == "POST":
        date = request.form["date"]
        category = request.form["category"]
        item_name = request.form["item_name"]
        description = request.form.get("description", "")
        amount = float(request.form["amount"])
        type_ = request.form["type"]
        taxrate = float(request.form.get("taxrate", 30)) / 100

        success, message = logic.update_transaction(id, date, category, item_name, amount, description, type_, taxrate)
        flash(message, "success" if success else "danger")
        return redirect(url_for("index"))

    return render_template("add_edit.html", transaction=transaction, categories=database.get_categories())

@app.route("/radera/<int:id>", methods=["POST"])
@require_auth
def delete_transaction(id):
    database.delete_info(id)
    flash("Transaktionen har raderats.", "success")
    return redirect(url_for("index"))

@app.route("/export/excel")
@require_auth
def export_excel():
    filename = "exporterade_transaktioner.xlsx"
    database.export_to_excel(filename)
    return send_file(filename, as_attachment=True)

@app.route("/import", methods=["GET", "POST"])
@require_auth
def import_transactions():
    if request.method == "POST":
        file = request.files["file"]
        if file and file.filename.endswith((".csv", ".xlsx")):
            filepath = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
            file.save(filepath)
            success, message = logic.import_from_file(filepath)
            flash(message, "success" if success else "danger")
            return redirect(url_for("index"))
    return render_template("import.html")

@app.route("/statistik", methods=["GET"])
@require_auth
def statistics():
    från = request.args.get("från")
    till = request.args.get("till")

    transaktioner = database.get_monthly_transactions()

    if från:
        transaktioner = [t for t in transaktioner if t[0] >= från]
    if till:
        transaktioner = [t for t in transaktioner if t[0] <= till]

    månader = sorted(set(t[0] for t in database.get_monthly_transactions()))

    return render_template("statistics.html",
        transactions=transaktioner,
        från=från,
        till=till,
        månader=månader
    )

@app.route("/unlock", methods=["POST"])
def unlock():
    file = session.get("file")
    if file:
        lock_path = os.path.join(os.path.dirname(file), LOCK_FILENAME)
        print(f"[DEBUG] Försöker ta bort låsfil: {lock_path}")
        try:
            if os.path.exists(lock_path):
                os.remove(lock_path)
                print("[DEBUG] Låsfil borttagen.")
        except Exception as e:
            print(f"[ERROR] Kunde inte ta bort låsfil: {e}")
    session.clear()
    return "", 204

# ✅ This block only runs in development
if __name__ == "__main__":
    database.init_db()
    app.run(debug=True)
