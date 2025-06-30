CREATE TABLE DOMAINE (
    id_domaine NUMBER PRIMARY KEY,
    nom_domaine VARCHAR2(100) NOT NULL
);
CREATE TABLE SPECIALITE (
    id_specialite NUMBER PRIMARY KEY,
    nom_specialite VARCHAR2(100) NOT NULL,
    id_domaine NUMBER,
    FOREIGN KEY (id_domaine) REFERENCES DOMAINE(id_domaine)
);
CREATE TABLE METIER (
    id_metier NUMBER PRIMARY KEY,
    nom_metier VARCHAR2(100) NOT NULL,
    id_specialite NUMBER,
    FOREIGN KEY (id_specialite) REFERENCES SPECIALITE(id_specialite)
);
CREATE TABLE REGION (
    id_region NUMBER PRIMARY KEY,
    nom_region VARCHAR2(100) NOT NULL
);
CREATE TABLE OFFRE_EMPLOI (
    id_offre NUMBER PRIMARY KEY,
    titre VARCHAR2(200),
    date_offre DATE,
    entreprise VARCHAR2(100),
    id_metier NUMBER,
    id_region NUMBER,
    description CLOB,
    source_site VARCHAR2(100),
    FOREIGN KEY (id_metier) REFERENCES METIER(id_metier),
    FOREIGN KEY (id_region) REFERENCES REGION(id_region)
);
CREATE TABLE COMPETENCE (
    id_competence NUMBER PRIMARY KEY,
    nom_competence VARCHAR2(100) UNIQUE
);
CREATE TABLE COMPETENCE_OFFRE (
    id_offre NUMBER,
    id_competence NUMBER,
    FOREIGN KEY (id_offre) REFERENCES OFFRE_EMPLOI(id_offre),
    FOREIGN KEY (id_competence) REFERENCES COMPETENCE(id_competence),
    PRIMARY KEY (id_offre, id_competence)
);
CREATE TABLE COMPETENCE_METIER (
    id_metier NUMBER,
    id_competence NUMBER,
    niveau_recommande VARCHAR2(50),
    FOREIGN KEY (id_metier) REFERENCES METIER(id_metier),
    FOREIGN KEY (id_competence) REFERENCES COMPETENCE(id_competence),
    PRIMARY KEY (id_metier, id_competence)
);
CREATE TABLE COMPETENCE_SPECIALITE (
    id_specialite NUMBER,
    id_competence NUMBER,
    FOREIGN KEY (id_specialite) REFERENCES SPECIALITE(id_specialite),
    FOREIGN KEY (id_competence) REFERENCES COMPETENCE(id_competence),
    PRIMARY KEY (id_specialite, id_competence)
);
