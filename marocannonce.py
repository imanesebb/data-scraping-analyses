from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import requests
import re
import unicodedata

DOMAINE_MAPPING = {
    "informatique": {
        "specialites": [
            "développement", "programmation", "développement web", "développement mobile", "fullstack", 
            "backend", "frontend", "IA", "intelligence artificielle", "machine learning", "deep learning",
            "data", "big data", "data science", "data engineering", "analyse de données", "visualisation de données",
            "cloud", "cloud computing", "AWS", "Azure", "GCP", "Google Cloud", "DevOps", "CI/CD", "virtualisation",
            "sécurité", "cybersécurité", "sécurité informatique", "cryptographie", "forensique", 
            "réseaux", "réseaux informatiques", "architecture réseau", "wifi", "LAN", "WAN",
            "systèmes embarqués", "robotique", "automatisation", "IOT", "internet des objets",
            "ERP", "SAP", "CRM", "base de données", "SQL", "Oracle", "NoSQL", "MongoDB",
            "ingénierie logicielle", "architecture logicielle", "conception orientée objet", "modélisation UML",
            "tests logiciels", "QA", "TDD", "BDD", "tests automatisés",
            "support technique", "technicien helpdesk", "maintenance informatique",
            "UX", "UI", "design", "expérience utilisateur", "interface utilisateur"
        ],
        "metiers": [
            "développeur", "développeur web", "développeur mobile", "développeur backend", "développeur frontend",
            "développeur fullstack", "data analyst", "data scientist", "data engineer", "ML engineer",
            "architecte cloud", "ingénieur cloud", "devops", "administrateur systèmes", "administrateur réseau",
            "ingénieur sécurité", "analyste SOC", "pentester", "expert cybersécurité",
            "chef de projet informatique", "scrum master", "product owner", "testeur logiciel", "QA engineer",
            "consultant ERP", "consultant SAP", "ingénieur logiciel", "architecte logiciel",
            "technicien support", "technicien informatique", "intégrateur web", "UI designer", "UX designer",
            "formateur informatique", "consultant IT", "responsable IT", "analyste fonctionnel", "business analyst","ingénieur"
        ]
    },

    "finance": {
        "specialites": [
            "comptabilité", "comptabilité générale", "comptabilité analytique", "audit", "audit interne",
            "audit externe", "contrôle de gestion", "analyse financière", "gestion budgétaire",
            "gestion de trésorerie", "trésorerie", "finance d'entreprise", "financement", "levée de fonds",
            "banque", "services bancaires", "analyse de crédit", "épargne", "crédit", "assurance", "assurance vie",
            "marchés financiers", "bourse", "investissement", "gestion d'actifs", "gestion de portefeuille",
            "gestion de patrimoine", "fiscalité", "optimisation fiscale", "conformité", "risques financiers",
            "AML", "lutte anti-blanchiment", "réglementation financière", "normes IFRS", "normes comptables",
            "fintech", "blockchain", "finance numérique", "paiements électroniques", "cryptomonnaie"
        ],
        "metiers": [
            "comptable", "expert-comptable", "auditeur", "auditeur interne", "auditeur externe",
            "contrôleur de gestion", "analyste financier", "analyste crédit", "risk manager", 
            "gestionnaire de portefeuille", "gestionnaire de patrimoine", "trésorier", "conseiller financier",
            "conseiller bancaire", "agent de crédit", "banquier", "courtier", "assureur", "actuaire",
            "responsable conformité", "analyste KYC", "analyste AML", "consultant fiscal", 
            "consultant financier", "trader", "analyste marché", "analyste risques", "chef comptable",
            "responsable financier", "DAF", "directeur administratif et financier"
        ]
    }
}


def normalize_text(text):
    # Lowercase, remove accents, extra spaces
    text = text.lower().strip()
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
    return text

def classify_job(title, description):
    title_text = normalize_text(title)
    desc_text = normalize_text(description)

    best_match = {
        "domaine": "Autre",
        "specialite": "Autre",
        "metier": "Autre",
        "score": 0
    }

    for domaine, spec_data in DOMAINE_MAPPING.items():
        for specialite in spec_data["specialites"]:
            spec_norm = normalize_text(specialite)
            if spec_norm in desc_text:  # ← specialite comes from description only
                for metier in spec_data["metiers"]:
                    metier_norm = normalize_text(metier)
                    score = 0
                    if metier_norm in title_text:  # ← metier comes from title only
                        score += 2  # bonus if metier found
                    if score > best_match["score"]:
                        best_match = {
                            "domaine": domaine.capitalize(),
                            "specialite": specialite.capitalize(),
                            "metier": metier.capitalize(),
                            "score": score
                        }

    # Only keep jobs that had a relevant metier in the title
    if best_match["score"] == 0:
        return None, None, None

    return best_match["domaine"], best_match["specialite"], best_match["metier"]


def clean_description(text):
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        line = line.strip()
        if any(line.lower().startswith(prefix) for prefix in [
            "niveau d'études", "ville", "répondre", "imprimer", "signaler",
            "contact", "téléphone", "annonceur", "email", "publiée le"
        ]):
            continue
        if line:
            cleaned.append(line)
    return ' '.join(cleaned)
def extract_skills(text):
    # Define a basic list of skills (can be expanded)
    known_skills = [
       # Programming Languages
        "python", "java", "javascript", "c", "c++", "c#", "php", "typescript", "go", "ruby", "r", "swift", "kotlin", "bash", "perl", "matlab",
        
        "html", "css", "sass", "bootstrap", "react", "angular", "next.js", "nuxt.js", "node.js", "express.js", "laravel", "symfony", "django", "flask",

        # Mobile Development
        "android", "ios", "react native", "flutter", "xamarin",

        # DevOps & Infrastructure
        "docker", "kubernetes", "ansible", "terraform", "jenkins", "github actions", "gitlab ci", "circleci", "ci/cd", "devops",

        # Cloud Platforms
        "aws", "azure", "gcp", "google cloud", "cloud computing", "firebase", "heroku", "digitalocean",

        # Databases
        "sql", "mysql", "postgresql", "oracle", "mariadb", "sqlite", "mongodb", "cassandra", "dynamodb", "redis", "nosql",

        # Data Science / AI
        "pandas", "numpy", "scipy", "matplotlib", "seaborn", "scikit-learn", "tensorflow", "keras", "pytorch", "xgboost", "lightgbm", "opencv",
        "machine learning", "deep learning", "data science", "data mining", "nlp", "computer vision",

        # Big Data
        "hadoop", "spark", "hive", "pig", "oozie", "sqoop", "kafka", "flink", "scala",

        # System & Network
        "linux", "windows server", "bash scripting", "powershell", "tcp/ip", "dns", "dhcp", "vpn", "firewall", "wireshark", "nagios",

        # Cybersecurity
        "cybersecurity", "network security", "penetration testing", "ethical hacking", "firewall", "siem", "splunk", "nmap", "burp suite", "metasploit",

        # Version Control
        "git", "svn", "github", "gitlab", "bitbucket",

        # Agile & Tools
        "jira", "trello", "confluence", "scrum", "kanban", "agile", "uml", "merise", "draw.io",

        # UI/UX & Design
        "ux", "ui", "figma", "adobe xd", "photoshop", "illustrator", "design thinking", "prototyping",

        # Testing
        "selenium", "cypress", "jest", "mocha", "chai", "junit", "pytest", "tdd", "bdd",

        # Other
        "erp", "sap", "crm", "zoho", "salesforce", "rpa", "uipath", "blueprism", "automation anywhere", "chatgpt", "openai", "api", "rest", "soap", "graphql",
        "comptabilité", "comptabilité générale", "comptabilité analytique", "grand livre", "bilan", "états financiers", "journal comptable", "déclaration fiscale",

        # Audit & Contrôle
        "audit interne", "audit externe", "contrôle de gestion", "réconciliation", "fraude", "conformité", "internal control", "sox", "coso",

        # Financial Analysis
        "analyse financière", "ratios financiers", "analyse des états financiers", "rentabilité", "flux de trésorerie", "modélisation financière", "valuation", "due diligence",

        # Budgeting & Forecasting
        "prévisions", "budgets", "gestion budgétaire", "planification financière", "reporting", "business plan", "tableaux de bord",

        # Treasury & Cash Management
        "trésorerie", "gestion de trésorerie", "flux de trésorerie", "paiements", "encaissements", "caisse", "prévisions de trésorerie",

        # Banking & Insurance
        "banque", "assurance", "épargne", "crédit", "analyse de crédit", "risques bancaires", "prêts", "leasing", "microfinance",

        # Markets & Investment
        "marchés financiers", "trading", "gestion de portefeuille", "gestion d’actifs", "bourse", "obligations", "actions", "forex", "crypto", "blockchain", "nft", "ethereum", "bitcoin",

        # Risk Management
        "gestion des risques", "risk management", "VaR", "credit risk", "market risk", "opérationnel risk", "AML", "KYC", "lutte anti-blanchiment", "réglementation",

        # Financial Tools & Software
        "excel", "power bi", "tableau", "vba", "sage", "sap fi/co", "quickbooks", "xero", "oracle finance", "hyperion", "erp", "crm",

        # Taxation & Legal
        "fiscalité", "optimisation fiscale", "tva", "impôts", "droits d’enregistrement", "IFRS", "normes IFRS", "normes comptables", "reporting réglementaire", "ba3", "bale", "solvabilité 2",

        # Soft skills (Finance-specific)
        "analyse", "rigueur", "sens du détail", "communication financière", "gestion du stress", "confidentialité"]

    found_skills = set()
    # Normalize description
    text = normalize_text(text)
    normalized_skills = [normalize_text(skill) for skill in known_skills]

    for norm_skill in normalized_skills:
        pattern = r"\b" + re.escape(norm_skill) + r"\b"
        if re.search(pattern, text):
            found_skills.add(norm_skill)


    return ', '.join(sorted(found_skills)) if found_skills else "Non spécifiées"

def scrape_jobs():
    jobs = []
    base_url = 'https://www.marocannonces.com/maroc/offres-emploi-b309.html'
    
    page = 1
    max_pages = 2# ⬅️ Change ce nombre selon combien de pages tu veux scraper

    while page <= max_pages:
        print(f"📄 Scraping page {page}...")
        if page == 1:
            url = base_url
        else:
            url = f'https://www.marocannonces.com/maroc/offres-emploi-b309.html?pge={page}'

        try:
            res = requests.get(url, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            offers = soup.select("ul.cars-list li")
            if not offers:
                print(f"🚫 Aucune offre trouvée sur la page {page}.")
                break
        except Exception as e:
            print(f"Erreur lors du chargement de la page {page} : {e}")
            break

        for offer in offers:
            a = offer.find("a", attrs={"title": True, "href": True})
            if not a:
                continue
            title = a['title'].strip()
            link = a['href'].strip()
            if not link.startswith('http'):
                link = 'https://www.marocannonces.com/' + link.lstrip('/')
            location_tag = offer.find("span", class_="location")
            location = location_tag.get_text(strip=True) if location_tag else "Non spécifiée"
            # Chercher la vraie date dans la fiche
              # Fallback si la vraie date n’est pas dans l’annonce
        
            try:
                job_response = requests.get(link, timeout=10)
                job_soup = BeautifulSoup(job_response.text, 'html.parser')
                description_tag = job_soup.find('div', class_='description')
                if description_tag:
                    raw_text = description_tag.get_text(separator=' ').strip()
                    raw_text = re.sub(r'\s+', ' ', raw_text)
                    description = raw_text
                    skills = extract_skills(raw_text)
                else:
                    description = "Description non disponible."
                    skills = []
            except Exception as e:
                print(f"Error fetching job detail page: {e}")
                description = "Erreur lors du chargement."
                skills = []
            # ✅ Extract publication date from <li> containing "Publiée le"
            from datetime import timedelta

            date_elem = job_soup.find('li', string=re.compile(r"publiée le", re.IGNORECASE))
            if date_elem:
                date_text = normalize_text(date_elem.get_text(strip=True))  # ← normalize accents
                # Example: "publiee le: 25 may - 13:01"
                
                # Handle special cases
                if "aujourd" in date_text:
                    date_obj = datetime.now()
                elif "hier" in date_text:
                    date_obj = datetime.now() - timedelta(days=1)
                else:
                    match = re.search(r'(\d{1,2})\s+([a-zéû]+)', date_text)
                    month_map = {
                        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
                    }

                    if match:
                        day = int(match.group(1))
                        raw_month = normalize_text(match.group(2))[:3]
                        month = month_map.get(raw_month, 1)
                        year = datetime.now().year % 100
                        date_obj = datetime.strptime(f"{year:02d}-{month:02d}-{day:02d}", "%y-%m-%d")
                    else:
                        date_obj = None
                    if not month:
                     print(f"❌ Mois inconnu: {raw_month} dans '{date_text}'")

                posted_date = date_obj.strftime("%d-%m-%Y") if date_obj else ""
            else:
                posted_date = ""


            domaine, specialite, metier = classify_job(title, description)

# Ignorer si le domaine est None = job non pertinent
            if not domaine:
                continue

            entreprise = "Inconnue"
            match = re.search(r"entreprise\s*[:\-]?\s*([A-Z][\w\s\-,.&]+?)(?:\s+salaire|[\n\r\.,;]|$)", description, re.IGNORECASE)
            if not match:
                match = re.search(r"société\s*[:\-]?\s*([A-Z][\w\s\-,.&]+?)(?:\s+salaire|[\n\r\.,;]|$)", description, re.IGNORECASE)
            if match:
                entreprise = match.group(1).strip().capitalize()

            jobs.append({
                "titre": title,
                "date_offre": posted_date,
                "entreprise": entreprise,
                "region": location,
                "domaine": domaine,
                "specialite": specialite,
                "metier": metier,
                "competences": skills,
                "source_site": "marocannonces.com",
                "url": link
            })

        page += 1
        time.sleep(1)  # petite pause entre les pages pour ne pas surcharger le serveur

    if not jobs:
        print("❌ Aucun job récupéré. Vérifie le HTML ou essaie d'inspecter la page.")
        return pd.DataFrame()

    df = pd.DataFrame(jobs)
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
    df = df[df['titre'].str.len() > 5]
    df.to_csv("marocannonce.csv", index=False, encoding='utf-8', errors='ignore')
    print("✅ Scraping terminé. Données enregistrées dans 'structured_jobs.csv'")
    return df

if __name__ == "__main__":
    scrape_jobs()
    print("Scraping finished successfully!")
