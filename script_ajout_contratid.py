import sqlite3

# 📂 Chemin vers ta base
db_path = "instance/database.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 👇 Ajoute la colonne contrat_id si elle existe pas déjà
try:
    cursor.execute('ALTER TABLE client ADD COLUMN contrat_id INTEGER')
    print("✅ Colonne 'contrat_id' ajoutée.")
except sqlite3.OperationalError:
    print("⚠️ Colonne 'contrat_id' existe déjà.")

conn.commit()
conn.close()
