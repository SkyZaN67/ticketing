import csv
import unicodedata
from app import app, db
from models import Client

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/database.db'  # ou le bon chemin


# 🔧 Fonction de nettoyage (accents, espaces, majuscules)
def normalize(text):
    if not text:
        return ""
    text = unicodedata.normalize('NFD', text.lower().strip())
    return ''.join(c for c in text if unicodedata.category(c) != 'Mn')

with app.app_context():
    with open('client2.csv', newline='', encoding='latin1') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        count_ok, count_fail = 0, 0

        for row in reader:
            nom_csv = normalize(row['Nom'])
            tel_csv = row['Téléphone fixe (facturation)'].strip().replace(" ", "")
            email = row['E-mail (facturation)'].strip()

            # Chercher parmi tous les clients existants
            found = False
            for client in Client.query.all():
                if normalize(client.nom) == nom_csv:
                    client.email = email
                    if tel_csv:
                        client.telephone = tel_csv
                    db.session.add(client)
                    print(f"✅ {client.nom} → {email} ({tel_csv})")
                    count_ok += 1
                    found = True
                    break

            if not found:
                print(f"❌ Pas trouvé : {row['Nom']}")
                count_fail += 1

        db.session.commit()
        print(f"\n✅ Mise à jour terminée : {count_ok} clients mis à jour, {count_fail} non trouvés.")
print("📂 BDD utilisée :", app.config['SQLALCHEMY_DATABASE_URI'])

