import pandas as pd
import re
import unicodedata
from pdfminer.high_level import extract_text

def normalize_text(text):
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    text = re.sub(r'[\W_]+', ' ', text)
    return text.lower()

def extract_text_from_pdf(filepath: str) -> str:
    try:
        raw_text = extract_text(filepath)
        return normalize_text(raw_text)
    except Exception as e:
        raise RuntimeError(f"Erreur de lecture du fichier PDF : {e}")

def fetch_jobs_with_competencies(conn):
    query = """
    SELECT o.id_offre,
           o.titre,
           o.entreprise,
           d.nom_domaine,
           s.nom_specialite,
           c.nom_competence
    FROM OFFRE_EMPLOI o
    JOIN METIER m             ON o.id_metier = m.id_metier
    JOIN SPECIALITE s         ON m.id_specialite = s.id_specialite
    JOIN DOMAINE d            ON s.id_domaine = d.id_domaine
    JOIN COMPETENCE_OFFRE co  ON co.id_offre = o.id_offre
    JOIN COMPETENCE c         ON co.id_competence = c.id_competence
    """
    df = pd.read_sql(query, conn)
    df.columns = df.columns.str.lower()
    grouped = df.groupby(
        ["id_offre", "titre", "entreprise", "nom_domaine", "nom_specialite"]
    )["nom_competence"].apply(list).reset_index()
    return grouped

def match_jobs(cv_text: str, conn):
    cv_tokens = set(cv_text.split())
    jobs_df = fetch_jobs_with_competencies(conn)

    matches = []
    for _, row in jobs_df.iterrows():
        comp_tokens = {normalize_text(c) for c in row.nom_competence}
        overlap = cv_tokens & comp_tokens
        score = (len(overlap) / len(comp_tokens)) * 100 if comp_tokens else 0
        matches.append({**row, "score": score})

    result_df = pd.DataFrame(matches).sort_values("score", ascending=False)
    return result_df[["titre", "entreprise", "nom_domaine", "nom_specialite", "score", "id_offre"]]