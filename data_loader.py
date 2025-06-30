import pandas as pd

def load_domain_data(conn):
    query = """
    WITH offres_with_site_type AS (
        SELECT
            o.date_offre,
            d.nom_domaine,
            s.nom_specialite,
            m.nom_metier,
            CASE WHEN o.source_site IN ('emploi.ma', 'marocannonces.com') THEN 'National'
                 ELSE 'International' END AS SITE_TYPE
        FROM OFFRE_EMPLOI o
        JOIN METIER m ON o.id_metier = m.id_metier
        JOIN SPECIALITE s ON m.id_specialite = s.id_specialite
        JOIN DOMAINE d ON s.id_domaine = d.id_domaine
        WHERE o.date_offre IS NOT NULL
    )
    SELECT
        TO_CHAR(date_offre, 'YYYY-MM') AS MOIS,
        TO_CHAR(date_offre, 'YYYY') AS ANNEE,
        nom_domaine,
        nom_specialite,
        SITE_TYPE,
        COUNT(*) AS NOMBRE_OFFRES
    FROM offres_with_site_type
    GROUP BY TO_CHAR(date_offre, 'YYYY-MM'),
             TO_CHAR(date_offre, 'YYYY'),
             nom_domaine,
             nom_specialite,
             SITE_TYPE
    ORDER BY MOIS, nom_domaine
    """
    df = pd.read_sql(query, conn)
    df = df[(df["NOM_SPECIALITE"] != "Autre") & (df["NOM_DOMAINE"].isin(["Finance", "Informatique"]))]

    # Add a global label manually
    df_global = df.copy()
    df_global["SITE_TYPE"] = "Global"
    df_combined = pd.concat([df, df_global], ignore_index=True)

    return df_combined


def load_competence_data(conn):
    query = """
    WITH offres_with_site_type AS (
        SELECT
            o.date_offre,
            d.nom_domaine,
            CASE 
                WHEN o.source_site IN ('emploi.ma', 'marocannonces.com') THEN 'National'
                ELSE 'International'
            END AS SITE_TYPE,
            c.nom_competence
        FROM OFFRE_EMPLOI o
        JOIN METIER m ON o.id_metier = m.id_metier
        JOIN SPECIALITE s ON m.id_specialite = s.id_specialite
        JOIN DOMAINE d ON s.id_domaine = d.id_domaine
        JOIN COMPETENCE_OFFRE co ON o.id_offre = co.id_offre
        JOIN COMPETENCE c ON co.id_competence = c.id_competence
        WHERE o.date_offre IS NOT NULL AND TRIM(c.nom_competence) IS NOT NULL
    )
    SELECT
        TO_CHAR(date_offre, 'YYYY-MM') AS MOIS,
        TO_CHAR(date_offre, 'YYYY') AS ANNEE,
        nom_domaine AS NOM_DOMAINE,
        SITE_TYPE,
        nom_competence AS COMPETENCE,
        COUNT(*) AS NB_OFFRES
    FROM offres_with_site_type
    GROUP BY 
        TO_CHAR(date_offre, 'YYYY-MM'),
        TO_CHAR(date_offre, 'YYYY'),
        nom_domaine,
        SITE_TYPE,
        nom_competence
    ORDER BY MOIS, NOM_DOMAINE, SITE_TYPE, NB_OFFRES DESC
    """
    df = pd.read_sql(query, conn)

    # Filtrer les domaines pertinents
    df = df[df["NOM_DOMAINE"].isin(["Finance", "Informatique"])]

    # Ajouter le label "Global"
    df_global = df.copy()
    df_global["SITE_TYPE"] = "Global"
    df_combined = pd.concat([df, df_global], ignore_index=True)

    return df_combined


def load_offre_competence_detail(conn):
    query = """
    SELECT
        o.id_offre,
        o.titre AS titre_offre,
        c.nom_competence AS competence
    FROM OFFRE_EMPLOI o
    JOIN COMPETENCE_OFFRE co ON o.id_offre = co.id_offre
    JOIN COMPETENCE c ON co.id_competence = c.id_competence
    WHERE o.titre IS NOT NULL
    """
    df = pd.read_sql(query, conn)
    return df

