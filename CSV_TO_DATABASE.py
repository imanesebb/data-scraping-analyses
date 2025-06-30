import oracledb
import csv
from datetime import datetime

# Connexion Oracle
connection = oracledb.connect(
    user="SYS",
    password="",
    dsn="",
    mode=oracledb.SYSDBA
)
cursor = connection.cursor()

# Fonction pour insérer ou récupérer un ID
def get_or_insert(table, column, value, id_column):
    cursor.execute(
        f"SELECT {id_column} FROM {table} WHERE {column} = :val",
        {'val': value}
    )
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute(f"SELECT NVL(MAX({id_column}), 0) + 1 FROM {table}")
    new_id = cursor.fetchone()[0]
    cursor.execute(
        f"INSERT INTO {table} ({id_column}, {column}) VALUES (:id, :val)",
        {'id': new_id, 'val': value}
    )
    return new_id

# Liste des fichiers CSV à traiter
csv_files = [
    "remoteok.csv",
    "emploima.csv",
    "marocannonce.csv",
    "joboom.csv",
]

for file in csv_files:
    print(f"🔄 Traitement du fichier : {file}")
    with open(file, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            region = (row.get("region") or "Inconnue").strip() or "Inconnue" 
            domaine = (row.get("domaine") or "Informatique").strip()
            specialite = (row.get("specialite") or "Général").strip()
            metier = (row.get("metier") or "").strip()
            if metier.lower() == "autre" or specialite.lower() == "autre":
                print(f"⏭️ Ligne ignorée (metier ou specialite = 'Autre') : {row}")
                continue
            date_offre_str = (row.get("date_offre") or "").strip()
            competences_raw = (row.get("competences") or "").strip()

            if not metier or not date_offre_str or not competences_raw:
                print(f"⏭️ Ligne ignorée (manque metier, date_offre ou competences) : {row}")
                continue

            date_obj = None
            date_offre_str = date_offre_str.replace(" ", "")
            try:
                if "." in date_offre_str:
                    date_obj = datetime.strptime(date_offre_str, "%d-%m-%Y").date()

                    

                else:
                    print(f"⏭️ Date au format inconnu, skipping row: {row}")
                    continue
            except ValueError:
                print(f"⏭️ Date invalide, skipping row: {row}")
                continue

            region_id = get_or_insert("REGION", "nom_region", region, "id_region")
            domaine_id = get_or_insert("DOMAINE", "nom_domaine", domaine, "id_domaine")

            # SPECIALITE
            cursor.execute(
                "SELECT id_specialite FROM SPECIALITE WHERE nom_specialite = :name AND id_domaine = :dom",
                {"name": specialite, "dom": domaine_id}
            )
            sp_row = cursor.fetchone()
            if sp_row:
                specialite_id = sp_row[0]
            else:
                cursor.execute("SELECT NVL(MAX(id_specialite), 0) + 1 FROM SPECIALITE")
                specialite_id = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO SPECIALITE (id_specialite, nom_specialite, id_domaine) VALUES (:id, :name, :dom)",
                    {"id": specialite_id, "name": specialite, "dom": domaine_id}
                )

            # METIER
            cursor.execute(
                "SELECT id_metier FROM METIER WHERE nom_metier = :name AND id_specialite = :sp",
                {"name": metier, "sp": specialite_id}
            )
            m_row = cursor.fetchone()
            if m_row:
                metier_id = m_row[0]
            else:
                cursor.execute("SELECT NVL(MAX(id_metier), 0) + 1 FROM METIER")
                metier_id = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO METIER (id_metier, nom_metier, id_specialite) VALUES (:id, :name, :sp)",
                    {"id": metier_id, "name": metier, "sp": specialite_id}
                )

            # OFFRE_EMPLOI
            cursor.execute("SELECT NVL(MAX(id_offre), 0) + 1 FROM OFFRE_EMPLOI")
            id_offre = cursor.fetchone()[0]

            entreprise = (row.get("entreprise") or "Entreprise non spécifiée")[:100].strip()
            description = (row.get("description") or "").strip()
            source_site = (row.get("source_site") or "non spécifié").strip()

            cursor.execute(
                """
                INSERT INTO OFFRE_EMPLOI (
                    id_offre, titre, date_offre, entreprise,
                    id_metier, id_region, description, source_site
                ) VALUES (
                    :id_offre, :titre, :date_offre, :entreprise,
                    :id_metier, :id_region, :description, :source_site
                )
                """,
                {
                    "id_offre": id_offre,
                    "titre": metier,
                    "date_offre": date_obj,
                    "entreprise": entreprise,
                    "id_metier": metier_id,
                    "id_region": region_id,
                    "description": description,
                    "source_site": source_site,
                }
            )

            # COMPETENCES
            separator = "-" if "jobboom" in file.lower() else ","
            competences = [c.strip() for c in competences_raw.split(separator) if c.strip()]
            for comp in competences:
                comp_truncated = comp[:100]
                comp_id = get_or_insert("COMPETENCE", "nom_competence", comp_truncated, "id_competence")

                cursor.execute(
                    "SELECT 1 FROM COMPETENCE_OFFRE WHERE id_offre = :id_offre AND id_competence = :id_comp",
                    {"id_offre": id_offre, "id_comp": comp_id}
                )
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO COMPETENCE_OFFRE (id_offre, id_competence) VALUES (:id_offre, :id_competence)",
                        {"id_offre": id_offre, "id_competence": comp_id}
                    )

# Finalisation
connection.commit()
cursor.close()
connection.close()
print("✅ Tous les fichiers ont été insérés avec succès dans Oracle.")
