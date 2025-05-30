import json
import os
from werkzeug.security import generate_password_hash

def skapa_hash(losenord):
    return generate_password_hash(losenord)

def spara_key_json(hashed_losenord, filnamn="key.json"):
    data = {"password": hashed_losenord}
    with open(filnamn, "w") as f:
        json.dump(data, f)
    print(f"\n✅ Filen '{filnamn}' har skapats med hashat lösenord.")

if __name__ == "__main__":
    losenord = input("Skriv in det lösenord du vill använda: ").strip()
    if not losenord:
        print("⚠️ Du måste skriva in ett lösenord.")
    else:
        hashed = skapa_hash(losenord)
        spara_key_json(hashed)

        print("\n🔐 Hash att använda i projektet (key.json):")
        print(json.dumps({"password": hashed}))
