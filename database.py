import sqlite3
import pandas as pd

DB_NAME = "budget.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Skapa kategori-tabell
    cur.execute("""
        CREATE TABLE IF NOT EXISTS category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL,
            type TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    # Skapa info-tabell med taxrate
    cur.execute("""
        CREATE TABLE IF NOT EXISTS info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            item_name TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL,
            taxrate REAL DEFAULT 0.3
        )
    """)

    # Lägg till kolumn taxrate om den saknas (bakåtkompatibilitet)
    cur.execute("PRAGMA table_info(info)")
    columns = [col[1] for col in cur.fetchall()]
    if "taxrate" not in columns:
        cur.execute("ALTER TABLE info ADD COLUMN taxrate REAL DEFAULT 0.3")

    conn.commit()
    conn.close()


# --- Info CRUD ---
def add_info(category, item_name, amount, date, description, type, taxrate=0.3):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Lägg till ny kategori om den inte finns
    cur.execute("SELECT 1 FROM category WHERE category_name = ?", (category,))
    if not cur.fetchone():
        cur.execute("INSERT INTO category (category_name, type, status) VALUES (?, ?, 'Aktiv')",
                    (category, type))

    cur.execute("""
        INSERT INTO info (category, item_name, amount, date, description, type, taxrate)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (category, item_name, amount, date, description, type, taxrate))
    conn.commit()
    conn.close()


def get_info():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM info ORDER BY date")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_info_by_id(id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM info WHERE id = ?", (id,))
    row = cur.fetchone()
    conn.close()
    return row


def update_info(id, category, item_name, amount, date, description, type, taxrate=0.3):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        UPDATE info
        SET category = ?, item_name = ?, amount = ?, date = ?, description = ?, type = ?, taxrate = ?
        WHERE id = ?
    """, (category, item_name, amount, date, description, type, taxrate, id))
    conn.commit()
    conn.close()


def delete_info(id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM info WHERE id = ?", (id,))
    conn.commit()
    conn.close()


# --- Exportera till Excel ---
def export_to_excel(filename):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("""
        SELECT date AS Datum,
               item_name AS Namn,
               category AS Kategori,
               amount AS Belopp,
               type AS Typ,
               description AS Beskrivning,
               taxrate AS Skattesats
        FROM info
        ORDER BY date
    """, conn)
    df.to_excel(filename, index=False)
    conn.close()


# --- Statistik ---
def get_monthly_summary():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT strftime('%Y-%m', date) AS månad,
               SUM(CASE WHEN type='Inkomst' THEN amount ELSE 0 END) AS inkomst,
               SUM(CASE WHEN type='Utgift' THEN amount ELSE 0 END) AS utgift,
               AVG(CASE WHEN type='Inkomst' THEN taxrate ELSE NULL END) AS taxrate
        FROM info
        GROUP BY månad
        ORDER BY månad
    """)
    rows = cur.fetchall()
    conn.close()

    resultat = []
    for månad, inkomst, utgift, taxrate in rows:
        taxrate = taxrate or 0.3
        if inkomst and inkomst > 0:
            brutto = inkomst / (1 - taxrate)
            skatt = brutto - inkomst
        else:
            brutto = 0
            skatt = 0
        resultat.append((månad, inkomst or 0, utgift or 0, brutto, skatt))
    return resultat


def get_monthly_transactions():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT strftime('%Y-%m', date) AS månad,
               item_name,
               amount,
               type,
               taxrate
        FROM info
        ORDER BY date
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

# --- Kategorier ---
def get_categories():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, category_name, type, status FROM category ORDER BY category_name")
    rows = cur.fetchall()
    conn.close()
    return rows


def add_category(name, type, status="Aktiv"):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT INTO category (category_name, type, status) VALUES (?, ?, ?)",
                (name, type, status))
    conn.commit()
    conn.close()
