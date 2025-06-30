from difflib import get_close_matches

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import csv
import re
import pandas as pd
import datetime

# 🔹 Compétences IT
skills_list_it = [
    "Python", "Java", "JavaScript", "SQL", "C++", "C#", "HTML", "CSS", "TypeScript",
    "React", "Angular", "Node.js", "Vue", "Django", "Flask", "FastAPI",
    "AWS", "Azure", "GCP", "Docker", "Kubernetes",
    "TensorFlow", "Pandas", "NumPy", "Scikit-learn", "Spark", "Hadoop",
    "PostgreSQL", "MongoDB", "MySQL", "Linux", "Git", "Jenkins", "CloudFlare"
    # Programming Languages
                                                      "python", "java", "javascript", "c", "c++", "c#", "php",
    "typescript", "go", "ruby", "r", "swift", "kotlin", "bash", "perl", "matlab",

    # Web Development
    "html", "css", "sass", "bootstrap", "react", "angular", "next.js", "nuxt.js", "node.js", "express.js", "laravel",
    "symfony", "django", "flask",

    # Mobile Development
    "android", "ios", "react native", "flutter", "xamarin",

    # DevOps & Infrastructure
    "docker", "kubernetes", "ansible", "terraform", "jenkins", "github actions", "gitlab ci", "circleci", "ci/cd",
    "devops",

    # Cloud Platforms
    "aws", "azure", "gcp", "google cloud", "cloud computing", "firebase", "heroku", "digitalocean",

    # Databases
    "sql", "mysql", "postgresql", "oracle", "mariadb", "sqlite", "mongodb", "cassandra", "dynamodb", "redis", "nosql",

    # Data Science / AI
    "pandas", "numpy", "scipy", "matplotlib", "seaborn", "scikit-learn", "tensorflow", "keras", "pytorch", "xgboost",
    "lightgbm", "opencv",
    "machine learning", "deep learning", "data science", "data mining", "nlp", "computer vision","Redshift", "Snowflake", "Big Query", "Presto", "Athena", "Spark", "DBT",

    # Big Data
    "hadoop", "spark", "hive", "pig", "oozie", "sqoop", "kafka", "flink", "scala",

    # System & Network
    "linux", "windows server", "bash scripting", "powershell", "tcp/ip", "dns", "dhcp", "vpn", "firewall", "wireshark",
    "nagios",

    # Cybersecurity
    "cybersecurity", "network security", "penetration testing", "ethical hacking", "firewall", "siem", "splunk", "nmap",
    "burp suite", "metasploit",

    # Version Control
    "git", "svn", "github", "gitlab", "bitbucket",

    # Agile & Tools
    "jira", "trello", "confluence", "scrum", "kanban", "agile", "uml", "merise", "draw.io",

    # UI/UX & Design
    "ux", "ui", "figma", "adobe xd", "photoshop", "illustrator", "design thinking", "prototyping",

    # Testing
    "selenium", "cypress", "jest", "mocha", "chai", "junit", "pytest", "tdd", "bdd"
]

# 🔹 Compétences Finance
skills_list_finance = [
    "Accounting", "Excel", "Finance", "Financial Modeling", "Tax", "IFRS", "Audit", "Budgeting",
    "Investment", "Portfolio", "Risk", "Banking", "CFA",
# Other
    "erp", "sap", "crm", "zoho", "salesforce", "rpa", "uipath", "blueprism", "automation anywhere", "chatgpt", "openai", "api", "rest", "soap", "graphql",

    # Accounting & Finance
    "accounting", "general accounting", "cost accounting", "general ledger", "balance sheet", "financial statements", "journal entry", "tax return",

    # Audit & Control
    "internal audit", "external audit", "management control", "reconciliation", "fraud", "compliance", "internal control", "sox", "coso",

    # Financial Analysis
    "financial analysis", "financial ratios", "financial statement analysis", "profitability", "cash flow", "financial modeling", "valuation", "due diligence",

    # Budgeting & Forecasting
    "forecasting", "budgets", "budget management", "financial planning", "reporting", "business plan", "dashboards",

    # Treasury & Cash Management
    "treasury", "cash management", "cash flow", "payments", "collections", "cash", "cash flow forecasting",

    # Banking & Insurance
    "banking", "insurance", "savings", "credit", "credit analysis", "bank risk", "loans", "leasing", "microfinance",

    # Markets & Investment
    "financial markets", "trading", "portfolio management", "asset management", "stock exchange", "bonds", "stocks", "forex", "crypto", "blockchain", "nft", "ethereum", "bitcoin",

    # Risk Management
    "risk management", "value at risk", "credit risk", "market risk", "operational risk", "aml", "kyc", "anti-money laundering", "regulation",

    # Financial Tools & Software
    "excel", "power bi", "tableau", "vba", "sage", "sap fi/co", "quickbooks", "xero", "oracle finance", "hyperion", "erp", "crm",

    # Taxation & Legal
    "taxation", "tax optimization", "vat", "taxes", "registration fees", "ifrs", "ifrs standards", "accounting standards", "regulatory reporting", "basel iii", "bale", "solvency ii",

    # Soft skills (Finance-specific)
    "analysis", "rigor", "attention to detail", "financial communication", "stress management", "confidentiality"

]

def extract_skills(description, skills_list):
    if not description or len(description.strip()) < 50:
        return ""  # Trop court, probablement non pertinent

    description_clean = description.lower()
    found = set()
    for skill in skills_list:
        pattern = rf"(?<![a-zA-Z]){re.escape(skill.lower())}(?![a-zA-Z])"
        if re.search(pattern, description_clean):
            found.add(skill)
    return ", ".join(sorted(found))

import re

def nettoyer_texte(titre):
    titre = re.sub(r'[^\w\s]', '', titre)
    titre = re.sub(r'\s+', ' ', titre).strip().lower()
    return titre

def detecter_metier(titre, metier_list):
    titre_nettoye = nettoyer_texte(titre)

    # Recherche exacte
    for mt in metier_list:
        if mt.lower() in titre_nettoye:
            return mt.title()

    # Recherche partielle : deux mots consécutifs
    mots = titre_nettoye.split()
    for i in range(len(mots) - 1):
        deux_mots = f"{mots[i]} {mots[i+1]}"
        if deux_mots in [m.lower() for m in metier_list]:
            return deux_mots.title()

    # Mot clé isolé
    for mot in mots:
        for mt in metier_list:
            if mot in mt.lower():
                return mt.title()

    # Fallback : 2 derniers mots
    return " ".join(mots[-2:]).title() if len(mots) >= 2 else titre.strip().title()


def extraire_info_titre(titre, tags=None):
    titre_lower = titre.lower()
    tags = tags or []

    domaines_it = ["developer", "engineer", "data", "cloud", "ai", "ml", "software", "cybersecurity", "devops", "fullstack", "backend", "frontend", "python", "java", "react"]
    domaines_finance = ["finance", "financial", "bank", "investment", "trading", "audit", "risk", "accounting", "cfa", "portfolio"]


    specialites_it = [ "development", "programming", "web development", "mobile development", "fullstack","full stack",
        "backend", "frontend", "AI", "artificial intelligence", "machine learning", "deep learning",
        "data", "big data", "data science", "data engineering", "data analysis", "data visualization",
        "cloud", "cloud computing", "AWS", "Azure", "GCP", "Google Cloud", "DevOps", "CI/CD", "virtualization",
        "security", "cybersecurity", "information security", "cryptography", "forensics",
        "networks", "computer networks", "network architecture", "wifi", "LAN", "WAN",
        "embedded systems", "robotics", "automation", "IoT", "internet of things",
        "ERP", "SAP", "CRM", "database", "SQL", "Oracle", "NoSQL", "MongoDB","software",
        "software engineering", "software architecture", "object-oriented design", "UML modeling",
        "software testing", "QA", "TDD", "BDD", "automated testing",
        "technical support", "helpdesk technician", "IT maintenance",
        "UX", "UI", "design", "user experience", "user interface"
                      ]
    specialites_finance = [
        "accounting", "general accounting", "cost accounting", "audit", "internal audit",
        "external audit", "management control", "financial analysis", "budget management",
        "treasury management", "treasury", "corporate finance", "funding", "fundraising",
        "banking", "banking services", "credit analysis", "savings", "credit", "insurance", "life insurance",
        "financial markets", "stock market", "investment", "asset management", "portfolio management",
        "wealth management", "taxation", "tax optimization", "compliance", "financial risks",
        "AML", "anti-money laundering", "financial regulation", "IFRS standards", "accounting standards",
        "fintech", "blockchain", "digital finance", "electronic payments", "cryptocurrency","Business Development", "NFTs","Sales"
    ]
    metiers_it = [
        "web developer", "backend developer", "frontend developer", "fullstack developer",
        "data scientist", "devops engineer", "software engineer", "security analyst",
        "cloud engineer", "machine learning engineer", "developer", "web developer", "mobile developer", "backend developer", "frontend developer",
        "fullstack developer", "data analyst", "data scientist", "data engineer", "ML engineer",
        "cloud architect", "cloud engineer", "devops engineer", "systems administrator", "network administrator",
        "security engineer", "SOC analyst", "pentester", "cybersecurity expert",
        "IT project manager", "scrum master", "product owner", "software tester", "QA engineer",
        "ERP consultant", "SAP consultant", "software engineer", "software architect",
        "support technician", "IT technician", "web integrator", "UI designer", "UX designer",
        "IT trainer", "IT consultant", "IT manager", "functional analyst", "business analyst", "engineer"

    ]
    metiers_finance = [
        "analyst", "manager", "consultant", "accountant", "auditor", "controller",
        "advisor", "specialist", "actuary", "treasurer", "economist","risk analyst", "financial analyst", "investment manager", "portfolio manager",
        "accounting specialist", "audit manager", "tax advisor", "budget analyst",
        "financial controller", "actuarial analyst", "accountant", "chartered accountant", "auditor", "internal auditor", "external auditor",
        "management controller", "financial analyst", "credit analyst", "risk manager",
        "portfolio manager", "wealth manager", "treasurer", "financial advisor",
        "bank advisor", "loan officer", "banker", "broker", "insurer", "actuary",
        "compliance officer", "KYC analyst", "AML analyst", "tax consultant",
        "financial consultant", "trader", "market analyst", "risk analyst", "chief accountant",
        "financial manager", "CFO", "chief financial officer", "Assistant"
    ]

    domaine = None
    for mot in domaines_it:
        if mot in titre_lower:
            domaine = "Informatique"
            break
    if domaine is None:
        for mot in domaines_finance:
            if mot in titre_lower:
                domaine = "Finance"
                break

        # Détection spécialité
    specialite = None
    specialite_list = specialites_it if domaine == "Informatique" else specialites_finance
    for sp in specialite_list:
        if re.search(r'\b' + re.escape(sp) + r'\b', titre_lower):
            specialite = sp.title()
            break
    if not specialite and tags:
        for tag in tags:
            for sp in specialite_list:
                if sp in tag.lower():
                    specialite = sp.title()
                    break
            if specialite:
                break
    if not specialite:
        for sp in specialite_list:
            if sp in titre_lower:
                specialite = sp.title()
                break
    if not specialite:
        specialite = "Autre"

    metier_list = metiers_it if domaine == "Informatique" else metiers_finance
    metier = detecter_metier(titre, metier_list)

    return {
        "domaine": domaine,
        "specialite": specialite,
        "metier": metier
    }

def scroll_down(driver, pause_time=2, max_scrolls=1):
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def scrape_jobs(driver, url, skills_list, domaine_label, max_jobs=10):
    driver.get(url)
    time.sleep(4)
    scroll_down(driver, pause_time=2, max_scrolls=1)

    job_rows = driver.find_elements(By.CSS_SELECTOR, "tr.job")
    print(f"🔍 {len(job_rows)} offres {domaine_label} trouvées sur {url}")

    results = []
    num_jobs = len(job_rows) if max_jobs is None else min(len(job_rows), max_jobs)
    for i in range(num_jobs):
        try:
            job_rows = driver.find_elements(By.CSS_SELECTOR, "tr.job")  # Recharger liste pour éviter stale
            row = job_rows[i]

            titre = row.find_element(By.CSS_SELECTOR, "h2").text.strip()
            entreprise = row.find_element(By.CSS_SELECTOR, "h3").text.strip()
            region = row.find_element(By.CSS_SELECTOR, ".location").text.strip() if row.find_elements(By.CSS_SELECTOR, ".location") else "Remote"
            date_iso = row.find_element(By.CSS_SELECTOR, "time").get_attribute("datetime")[:10]
            # Format date_offre as %d-%m-%Y
            try:
                date_offre = datetime.datetime.strptime(date_iso, "%Y-%m-%d").strftime("%d-%m-%Y")
            except Exception:
                date_offre = date_iso

            tags = [t.text.strip() for t in row.find_elements(By.CSS_SELECTOR, ".tags .tag") if t.text.strip()]

            infos = extraire_info_titre(titre, tags)
            domaine = infos["domaine"] if infos["domaine"] else domaine_label
            specialite = infos["specialite"]
            metier = infos["metier"]

            href = row.get_attribute("data-href")
            url_offre = "https://remoteok.com" + href if href else ""

            full_desc = ""
            if url_offre:
                # Ouvrir dans un nouvel onglet
                driver.execute_script(f"window.open('{url_offre}', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(2)
                try:
                    desc_element = driver.find_element(By.CSS_SELECTOR, "div.description")
                    full_desc = desc_element.text.strip()
                except:
                    full_desc = ""
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            skills = extract_skills(full_desc, skills_list)

            # Filtrage des compétences cohérentes avec le domaine
            if domaine == "Informatique":
                skills = ", ".join([s for s in skills.split(", ") if s in skills_list_it])
            elif domaine == "Finance":
                skills = ", ".join([s for s in skills.split(", ") if s in skills_list_finance])

            # Nettoyage région
            region_clean = "Nationale" if "maroc" in region.lower() else "Internationale"

            results.append([
                titre, date_offre, entreprise, region_clean,
                domaine, specialite, metier, skills,
                "remoteok.com", url_offre
            ])
        except Exception as e:
            print(f"❌ Erreur sur une offre {domaine_label} : {e}")
            continue
    return results

# --- CONFIG WebDriver ---
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


# --- SCRAPING ---
MAX_JOBS_PER_SITE = 10 # Change this value as needed

results_it_dev = scrape_jobs(driver, "https://remoteok.com/remote-dev-jobs", skills_list_it, "Informatique", max_jobs=MAX_JOBS_PER_SITE)
results_it_data = scrape_jobs(driver, "https://remoteok.com/remote-data-jobs", skills_list_it, "Informatique", max_jobs=MAX_JOBS_PER_SITE)
results_it = results_it_dev + results_it_data

results_finance = scrape_jobs(driver, "https://remoteok.com/remote-finance-jobs", skills_list_finance, "Finance", max_jobs=MAX_JOBS_PER_SITE)

# --- SAUVEGARDE ---
all_results = results_it + results_finance
with open("OUMAYMA.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "titre", "date_offre", "entreprise", "region",
        "domaine", "specialite", "metier", "skills",
        "source_site", "url"
    ])
    writer.writerows(all_results)

print(f"✅ Scraping terminé. {len(all_results)} offres sauvegardées dans 'remote.csv'")

driver.quit()

# --- DICTIONNAIRES DE TRADUCTION ---
metier_translation = {
    "developer": "développeur",
    "web developer": "développeur web",
    "mobile developer": "développeur mobile",
    "backend developer": "développeur backend",
    "frontend developer": "développeur frontend",
    "fullstack developer": "développeur fullstack",
    "data analyst": "data analyst",
    "data scientist": "data scientist",
    "data engineer": "data engineer",
    "ml engineer": "ML engineer",
    "cloud architect": "architecte cloud",
    "cloud engineer": "ingénieur cloud",
    "devops": "devops",
    "systems administrator": "administrateur systèmes",
    "network administrator": "administrateur réseau",
    "security engineer": "ingénieur sécurité",
    "soc analyst": "analyste SOC",
    "pentester": "pentester",
    "cybersecurity expert": "expert cybersécurité",
    "it project manager": "chef de projet informatique",
    "scrum master": "scrum master",
    "product owner": "product owner",
    "software tester": "testeur logiciel",
    "qa engineer": "QA engineer",
    "erp consultant": "consultant ERP",
    "sap consultant": "consultant SAP",
    "software engineer": "ingénieur logiciel",
    "software architect": "architecte logiciel",
    "support technician": "technicien support",
    "it technician": "technicien informatique",
    "web integrator": "intégrateur web",
    "ui designer": "UI designer",
    "ux designer": "UX designer",
    "it trainer": "formateur informatique",
    "it consultant": "consultant IT",
    "it manager": "responsable IT",
    "functional analyst": "analyste fonctionnel",
    "business analyst": "business analyst",
    "engineer": "ingénieur",
    "accountant": "comptable",
    "chartered accountant": "expert-comptable",
    "auditor": "auditeur",
    "internal auditor": "auditeur interne",
    "external auditor": "auditeur externe",
    "management controller": "contrôleur de gestion",
    "financial analyst": "analyste financier",
    "credit analyst": "analyste crédit",
    "risk manager": "risk manager",
    "portfolio manager": "gestionnaire de portefeuille",
    "wealth manager": "gestionnaire de patrimoine",
    "treasurer": "trésorier",
    "financial advisor": "conseiller financier",
    "bank advisor": "conseiller bancaire",
    "credit officer": "agent de crédit",
    "banker": "banquier",
    "broker": "courtier",
    "insurer": "assureur",
    "actuary": "actuaire",
    "compliance officer": "responsable conformité",
    "kyc analyst": "analyste KYC",
    "aml analyst": "analyste AML",
    "tax consultant": "consultant fiscal",
    "financial consultant": "consultant financier",
    "trader": "trader",
    "market analyst": "analyste marché",
    "risk analyst": "analyste risques",
    "chief accountant": "chef comptable",
    "financial manager": "responsable financier",
    "cfo": "DAF",
    "chief financial officer": "directeur administratif et financier"
}

specialite_translation = {
    # ... (use your full specialite_translation dictionary here) ...
    "developer": "développeur",
    "web developer": "développeur web",
    "mobile developer": "développeur mobile",
    "backend developer": "développeur backend",
    "frontend developer": "développeur frontend",
    "fullstack developer": "développeur fullstack",
    "data analyst": "data analyst",
    "data scientist": "data scientist",
    "data engineer": "data engineer",
    "ml engineer": "ML engineer",
    "cloud architect": "architecte cloud",
    "cloud engineer": "ingénieur cloud",
    "devops": "devops",
    "systems administrator": "administrateur systèmes",
    "network administrator": "administrateur réseau",
    "security engineer": "ingénieur sécurité",
    "soc analyst": "analyste SOC",
    "pentester": "pentester",
    "cybersecurity expert": "expert cybersécurité",
    "it project manager": "chef de projet informatique",
    "scrum master": "scrum master",
    "product owner": "product owner",
    "software tester": "testeur logiciel",
    "qa engineer": "QA engineer",
    "erp consultant": "consultant ERP",
    "sap consultant": "consultant SAP",
    "software engineer": "ingénieur logiciel",
    "software architect": "architecte logiciel",
    "support technician": "technicien support",
    "it technician": "technicien informatique",
    "web integrator": "intégrateur web",
    "ui designer": "UI designer",
    "ux designer": "UX designer",
    "it trainer": "formateur informatique",
    "it consultant": "consultant IT",
    "it manager": "responsable IT",
    "functional analyst": "analyste fonctionnel",
    "business analyst": "business analyst",
    "engineer": "ingénieur",
    "development": "développement",
    "programming": "programmation",
    "web development": "développement web",
    "mobile development": "développement mobile",
    "fullstack": "fullstack",
    "backend": "backend",
    "frontend": "frontend",
    "ai": "IA",
    "artificial intelligence": "intelligence artificielle",
    "machine learning": "machine learning",
    "deep learning": "deep learning",
    "data": "data",
    "big data": "big data",
    "data science": "data science",
    "data engineering": "data engineering",
    "data analysis": "analyse de données",
    "data visualization": "visualisation de données",
    "cloud": "cloud",
    "cloud computing": "cloud computing",
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "google cloud": "Google Cloud",
    "devops": "DevOps",
    "ci/cd": "CI/CD",
    "virtualization": "virtualisation",
    "security": "sécurité",
    "cybersecurity": "cybersécurité",
    "it security": "sécurité informatique",
    "cryptography": "cryptographie",
    "forensics": "forensique",
    "networks": "réseaux",
    "computer networks": "réseaux informatiques",
    "network architecture": "architecture réseau",
    "wifi": "wifi",
    "lan": "LAN",
    "wan": "WAN",
    "embedded systems": "systèmes embarqués",
    "robotics": "robotique",
    "automation": "automatisation",
    "iot": "IOT",
    "internet of things": "internet des objets",
    "erp": "ERP",
    "sap": "SAP",
    "crm": "CRM",
    "database": "base de données",
    "sql": "SQL",
    "oracle": "Oracle",
    "nosql": "NoSQL",
    "mongodb": "MongoDB",
    "software engineering": "ingénierie logicielle",
    "software architecture": "architecture logicielle",
    "object-oriented design": "conception orientée objet",
    "uml modeling": "modélisation UML",
    "software testing": "tests logiciels",
    "qa": "QA",
    "tdd": "TDD",
    "bdd": "BDD",
    "automated testing": "tests automatisés",
    "technical support": "support technique",
    "helpdesk technician": "technicien helpdesk",
    "it maintenance": "maintenance informatique",
    "ux": "UX",
    "ui": "UI",
    "design": "design",
    "user experience": "expérience utilisateur",
    "user interface": "interface utilisateur",
    "accounting": "comptabilité",
    "general accounting": "comptabilité générale",
    "analytical accounting": "comptabilité analytique",
    "audit": "audit",
    "internal audit": "audit interne",
    "external audit": "audit externe",
    "management control": "contrôle de gestion",
    "financial analysis": "analyse financière",
    "budget management": "gestion budgétaire",
    "cash management": "gestion de trésorerie",
    "treasury": "trésorerie",
    "corporate finance": "finance d'entreprise",
    "funding": "financement",
    "fundraising": "levée de fonds",
    "banking": "banque",
    "banking services": "services bancaires",
    "credit analysis": "analyse de crédit",
    "savings": "épargne",
    "credit": "crédit",
    "insurance": "assurance",
    "life insurance": "assurance vie",
    "financial markets": "marchés financiers",
    "stock exchange": "bourse",
    "investment": "investissement",
    "asset management": "gestion d'actifs",
    "portfolio management": "gestion de portefeuille",
    "wealth management": "gestion de patrimoine",
    "taxation": "fiscalité",
    "tax optimization": "optimisation fiscale",
    "compliance": "conformité",
    "financial risks": "risques financiers",
    "aml": "AML",
    "anti-money laundering": "lutte anti-blanchiment",
    "financial regulation": "réglementation financière",
    "ifrs standards": "normes IFRS",
    "accounting standards": "normes comptables",
    "fintech": "fintech",
    "blockchain": "blockchain",
    "digital finance": "finance numérique",
    "electronic payments": "paiements électroniques",
    "cryptocurrency": "cryptomonnaie"
}

def translate_value(value, translation_dict):
    if pd.isna(value):
        return value
    value_lower = value.strip().lower()
    lower_dict = {k.lower(): v for k, v in translation_dict.items()}
    for key in lower_dict:
        if key in value_lower:
            return lower_dict[key]
    return value

# --- TRADUCTION ET EXPORT CSV ---
columns = [
    "titre", "date_offre", "entreprise", "region",
    "domaine", "specialite", "metier", "competences",
    "source_site", "url"
]
df = pd.DataFrame(all_results, columns=columns)
# Apply translations
df["metier"] = df["metier"].apply(lambda x: translate_value(x, metier_translation))
df["specialite"] = df["specialite"].apply(lambda x: translate_value(x, specialite_translation))

# Save translated version
df.to_csv("oumayma.csv", index=False, encoding="utf-8")
print("✅ Traduction terminée. Fichier 'remoteok.csv' généré.")
