import database
import pandas as pd

def add_transaction(date, category, item_name, amount, description, type, taxrate):
    if not date or not item_name or amount <= 0:
        return False, "Ogiltiga värden!"
    database.add_info(category, item_name, amount, date, description, type, taxrate)
    return True, "Transaktion tillagd!"

def update_transaction(id, date, category, item_name, amount, description, type, taxrate):
    if not date or not item_name or amount <= 0:
        return False, "Ogiltiga värden!"
    database.update_info(id, category, item_name, amount, date, description, type, taxrate)
    return True, "Transaktion uppdaterad!"

def import_from_file(filepath):
    try:
        if filepath.endswith(".csv"):
            df = pd.read_csv(filepath, delimiter=";")
        elif filepath.endswith(".xlsx"):
            df = pd.read_excel(filepath)
        else:
            return False, "Ogiltig filtyp. Endast CSV eller Excel stöds."

        df.columns = [col.strip() for col in df.columns]
        mapping = {
            "Date": "Datum",
            "Description": "Beskrivning",
            "Amount": "Belopp",
            "Type": "Typ",
            "Item": "Namn",
            "Category": "Kategori"
        }
        df.rename(columns=mapping, inplace=True)

        required = ["Datum", "Namn", "Belopp", "Typ", "Kategori"]
        missing = [col for col in required if col not in df.columns]
        if missing:
            return False, f"Filen saknar kolumner: {', '.join(missing)}"

        for _, row in df.iterrows():
            database.add_info(
                str(row["Kategori"]),
                str(row["Namn"]),
                float(row["Belopp"]),
                str(row["Datum"]),
                str(row.get("Beskrivning", "")),
                str(row["Typ"])
            )
        return True, "Importen lyckades!"
    except Exception as e:
        return False, f"Fel vid import: {e}"
