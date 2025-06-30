from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime, timedelta
import re


skills_finance = [
    # Comptabilité & Finance
    "comptabilité", "finance", "gestion financière", "analyse financière", "contrôle budgétaire",
    "budgétisation", "suivi budgétaire", "prévision financière", "gestion des coûts", "comptabilité analytique",
    "audit", "audit interne", "audit externe", "états financiers", "IFRS", "GAAP", "CPA", "CMA", "MBA", 
    "normes comptables", "normes fiscales", "déclarations fiscales", "gestion des immobilisations",
    
    # Analyse & Modélisation
    "modélisation financière", "analyse de rentabilité", "analyse de performance", 
    "indicateurs financiers", "KPI", "tableaux de bord", "reporting", "power bi", "excel avancé", "tableaux croisés dynamiques",
    
    # Systèmes & ERP
    "ERP", "SAP", "Oracle Financials", "QuickBooks", "SAGE", "Serti", "JD Edwards", "Microsoft Dynamics",
    "Suite Office", "Excel", "Word", "PowerPoint", "Outlook",

    # Outils de gestion & contrôle
    "contrôle interne", "politique financière", "procédures comptables", "clôture mensuelle",
    "gestion de trésorerie", "flux de trésorerie", "rapprochement bancaire", "gestion des risques financiers",

    # Administration et RH en finance
    "administration", "gestion administrative", "paie", "ressources humaines", "recrutement", "politiques RH",
    "documentation RH", "gestion des documents", "coordination d'équipe", "gestion d'activités sociales",


]


domain_keywords_finance = {
    "comptabilité": [
        "comptabilité", "comptable", "audit", "états financiers", "écritures comptables", 
        "déclarations fiscales", "rapprochement bancaire", "normes comptables", "IFRS", "GAAP", 
        "CPA", "fiscalité", "Serti", "QuickBooks", "clôture mensuelle", "comptes clients", "comptes fournisseurs" ,"gestion de portefeuille", "gestion d'actifs", "allocation d’actifs", "titres boursiers", "produits financiers",
        "marchés financiers", "instruments financiers", "analyse de portefeuille", "risque de marché", "bourse",
        "Bloomberg", "Reuters", "fiducie", "gestion collective"
    ],
    "contrôle financier": [
        "contrôleur", "contrôle financier", "états financiers", "normes IFRS", "clôture mensuelle", "audit interne",
        "audit externe", "budget", "prévision", "reporting financier", "analyse de variance", "contrôle interne",
        "gestion de trésorerie", "indicateurs de performance", "fiscalité", "conformité", "SAP", "Oracle", "JD Edwards",
    ],
    "accréditation et cautionnement": [
        "cautionnement", "accréditation", "analyse crédit", "solvabilité", "souscription", "garantie bancaire",
        "analyse de risque", "documents juridiques", "analyse financière", "évaluation du risque", "procédure d'accréditation"
    ],
    "analyse financière et FP&A": [
        "fp&a", "analyse financière", "modélisation financière", "business partnering", "kpi", "prévisions",
    "forecast", "scénario", "budget", "rentabilité", "automatisation du reporting", "excel avancé", "power bi",
    "tableau", "looker", "sql", "analyse des marges", "analyse de variance", "analyste financier", "analyste performance financière", "analyste fp&a", "analyste financier fp&a", "analyste performance", "analyste senior"

    ],
"support": [
    "support","technicien","technicien(ne)","technicien informatique","helpdesk","service desk","assistance","soutien","télémaintenance","incident","ticketing","résolution","hardware","logiciel","client","utilisateur","poste de travail","windows","mac","linux","formation utilisateur",
    "gestionnaire de parc","gestion de parc","maintenance","dépannage","intervention","hotline","bureautique","technicien support","technicien helpdesk","technicien service desk","technicien assistance","technicien maintenance"
],



    "contrôle de gestion": [
        "contrôle budgétaire", "gestion de coûts", "coûts de production", "suivi budgétaire", 
        "contrôle interne", "procédures", "politique financière"
    ],
    "ERP & logiciels comptables": [
        "ERP", "SAP", "Oracle", "SAGE", "JD Edwards", "Serti", "Microsoft Dynamics", 
        "logiciel comptable", "QuickBooks", "Excel", "Power BI"
    ],
    "gestion des ressources humaines": [
        "ressources humaines", "paie", "recrutement", "documentation RH", "politique RH", 
        "coordination", "activités sociales", "gestion du personnel" ,"analyse des écarts", "suivi des coûts", "rentabilité produit", "tableaux de bord", "coûts de revient",
        "centre de coûts", "suivi budgétaire", "gestion budgétaire", "clôture analytique", "ERP", "indicateurs financiers"
    ],
    "administration financière": [
        "gestion administrative", "direction financière", "gestion de département", 
        "organisation", "gestion de projets financiers"
    ],
    
    "assistant-contrôle / technicien": [
        "assistant-contrôleur", "rapprochements bancaires", "écritures comptables", "saisie comptable", "support au contrôle",
        "reporting", "suivi de trésorerie", "analyse simple", "immobilisations", "comptabilité générale", "comptabilité auxiliaire"
    ],
    "direction financière et investissements": [
        "directeur financier", "directeur finance", "gestion des investissements", "stratégie financière", "levée de fonds",
        "fusions et acquisitions", "M&A", "relation investisseurs", "trésorerie stratégique", "analyse stratégique",
        "pilotage financier", "gouvernance", "gestion des actifs", "risque financier", "analyse de rentabilité"
    ]
}





finance_job_categories = {
    "Comptable": [
        "comptable", "expert-comptable", "comptabilité", "accountant", "auditeur", "audit", "auditrice"
    ],
    "Contrôleur financier": [
        "contrôleur financier", "contrôle financier", "contrôleur de gestion", "contrôle de gestion", "financial controller"
    ],
    "Analyste financier": [
        "analyste financier", "analyse financière", "financial analyst", "analyste performance financière", "analyste fp&a", "fp&a"
    ],
    "Directeur financier": [
        "directeur financier", "directrice financière", "cfo", "chief financial officer"
    ],
    "Gestionnaire de portefeuille": [
        "gestionnaire de portefeuille", "portfolio manager", "gestion de portefeuille"
    ],
    "Gestionnaire de risques": [
        "gestionnaire de risques", "risk manager", "gestion des risques", "analyste risques"
    ],
    "Trésorier": [
        "trésorier", "trésorerie", "treasurer", "gestion de trésorerie"
    ],
    "Contrôleur de gestion": [
        "contrôleur de gestion", "contrôle de gestion", "contrôle budgétaire", "contrôle interne"
    ],
    "Fiscaliste": [
        "fiscaliste", "fiscalité", "tax specialist", "tax manager"
    ],
    "Responsable paie": [
        "responsable paie", "gestionnaire paie", "payroll manager", "gestion de la paie"
    ],
    "Analyste crédit": [
        "analyste crédit", "credit analyst", "analyse crédit", "gestion du crédit"
    ],
    "Chargé de recouvrement": [
        "chargé de recouvrement", "recouvrement", "collection specialist"
    ],
    "Gestionnaire administratif": [
        "gestionnaire administratif", "administration financière", "gestion administrative", "administrateur financier"
    ],
    "Assistant comptable": [
        "assistant comptable", "assistante comptable", "aide-comptable", "assistant-contrôleur"
    ],
    "Conseiller financier": [
        "conseiller financier", "conseillère financière", "financial advisor", "conseiller en gestion de patrimoine"
    ],
    "Gestionnaire d’actifs": [
        "gestionnaire d’actifs", "asset manager", "gestion d’actifs"
    ],
    "Analyste en investissement": [
        "analyste en investissement", "investment analyst", "analyste investissement"
    ],
    "Responsable administratif et financier": [
        "responsable administratif et financier", "raf", "administrative and financial manager"
    ],
    "Contrôleur budgétaire": [
        "contrôleur budgétaire", "contrôle budgétaire", "budget controller"
    ],
    "Assistant administratif": [
        "assistant administratif", "assistante administrative", "administrative assistant"
    ],
    "Gestionnaire de paie": [
        "gestionnaire de paie", "payroll manager", "gestion de la paie"
    ],
    "Analyste conformité": [
        "analyste conformité", "compliance analyst", "conformité"
    ],
    "Gestionnaire de fonds": [
        "gestionnaire de fonds", "fund manager", "gestion de fonds"
    ],
    "Analyste reporting": [
        "analyste reporting", "reporting analyst", "reporting financier"
    ],
    "Assistant de gestion": [
        "assistant de gestion", "assistante de gestion", "gestion assistant"
    ],
    "Analyste trésorerie": [
        "analyste trésorerie", "treasury analyst", "analyse trésorerie"
    ],
    "Responsable facturation": [
        "responsable facturation", "billing manager", "gestion de la facturation"
    ],
    "Analyste contrôle de gestion": [
        "analyste contrôle de gestion", "contrôle de gestion analyst", "analyste contrôle"
    ],
    "Gestionnaire de contrats": [
        "gestionnaire de contrats", "contract manager", "gestion des contrats"
    ],
    "Analyste budgétaire": [
        "analyste budgétaire", "budget analyst", "analyse budgétaire"
    ],
    "Analyste risques": [
        "analyste risques", "risk analyst", "analyse de risques"
    ]
    # Tu peux ajouter d'autres métiers selon tes besoins
}
ALL_skills = [
    # Développement & Programmation
    "Java", "JavaScript", "TypeScript", "Python", "C++", "C#", "VB.NET", ".NET Core",
    "Node.js", "React.js", "Angular", "Vue.js", "HTML", "CSS", "SCSS", "SASS",
    "XML", "JSON", "RESTful APIs", "SOAP APIs", "GraphQL", "PHP", "Kotlin", "Swift",
    "Go", "Rust", "Bash", "Shell scripting", "PowerShell", "SQL", "NoSQL", "MongoDB",
    "Cassandra", "Redis", "RPG ILE", "CLLE", "Free-form RPG", "COBOL", "GIT", "GitHub",
    "GitLab", "Gitflow", "RDI", "Eclipse", "Visual Studio", "VS Code", "IntelliJ IDEA",
    "Eclipse RCP", "Maven", "Gradle", "Ant", "NPM", "Yarn", "Webpack", "Babel",
    "Jest", "Mocha", "NUnit", "JUnit", "xUnit", "Selenium", "Cypress", "CI/CD",
    "Jenkins", "GitHub Actions", "GitLab CI", "CircleCI", "Docker", "Kubernetes",
    "OpenShift", "Helm",

    # Systèmes & Infrastructure
    "VMware ESXi", "vSphere", "Hyper-V", "Proxmox", "VirtualBox", "Vagrant", "Unix",
    "Linux", "Windows Server", "Windows 10", "Windows 11", "Active Directory", "Entra ID",
    "Intune", "Microsoft Exchange", "Office 365", "Azure Portal", "Google Workspace",
    "SCCM", "WSUS", "Commvault", "Zerto", "Veeam", "Ansible", "Puppet", "Chef", "Terraform",
    "Nagios", "Zabbix", "Prometheus", "Grafana", "Splunk", "ELK Stack", "ServiceNow",
    "GLPI", "OTRS", "Apache", "Nginx", "Tomcat", "IIS", "GlassFish", "Wildfly", "JBoss",
    "MQ", "Kafka", "RabbitMQ",

    # Réseaux & Télécom
    "TCP/IP", "UDP", "OSPF", "BGP", "RIP", "VLAN", "MPLS", "NAT", "PAT", "DHCP", "DNS",
    "GPON", "FTTH", "FTTB", "SFP", "SFP+", "QSFP", "Fibre optique", "LAN", "WAN", "MAN",
    "Wifi", "Bluetooth", "NFC", "ZigBee", "RF", "micro-ondes", "satellite GEO", "satellite LEO",
    "IPSEC", "SSL", "TLS", "VPN", "OpenVPN", "WireGuard", "L2TP/IPSEC", "QoS", "DiffServ",
    "ToS", "SD-WAN", "Load Balancing", "Firewalls", "Cisco IOS", "JunOS", "Wireshark",
    "SNMP", "NetFlow", "sFlow",

    # Cloud & Infonuagique
    "Microsoft Azure", "Amazon AWS", "Google Cloud Platform", "IBM Cloud", "Oracle Cloud",
    "IaaS", "PaaS", "SaaS", "Azure Functions", "AWS Lambda", "AppSheet", "PowerApps",
    "Azure DevOps", "CloudFormation", "ARM Templates", "CloudWatch", "Azure Monitor",

    # Analyse, Fonctionnel & Gestion
    "Analyse fonctionnelle", "Spécifications fonctionnelles", "Spécifications techniques",
    "SDLC", "UML", "BPMN", "Agile", "DevOps", "ITIL", "Lean", "Prince2", "Design thinking",
    "Jira", "Confluence", "Trello", "Asana",

    # Cybersécurité
    "MFA", "2FA", "AES", "RSA", "ECC", "OWASP", "CSPM", "CASB", "IAM", "SIEM", "Firewall",
    "IDS", "IPS", "Nessus", "Qualys", "PKI", "Certificats SSL",

    # Data & Business Intelligence
    "Power BI", "Tableau", "Qlik Sense", "Excel avancé", "VBA", "Pandas", "NumPy", "ETL",
    "Talend", "Informatica", "SSIS", "RDBMS", "Data warehouse", "Redshift", "BigQuery",
    "Snowflake", "Data Lake", "HDFS", "Spark", "Hadoop", "FastAPI", "Flask", "R", "SAS",

]





IT_job_categories = {
    "Développeur": [
        "développeur", "developpeur", "développeuse", "developpeuse", "software developer", "web developer", "fullstack", "backend", "frontend", "programmeur", "programmation"
    ],
    "Ingénieur logiciel": [
        "ingénieur logiciel", "software engineer", "architecte logiciel", "architecte technique"
    ],
    "DevOps": [
        "devops", "site reliability engineer", "SRE", "cloud engineer", "ingénieur cloud", "ingénieur devops"
    ],
    "Testeur / QA": [
        "testeur", "qa", "quality assurance", "ingénieur test", "test engineer", "automatisation des tests"
    ],
    "Chef de projet": [
        "chef de projet", "project manager", "chef de projet technique", "chef de projet informatique", "scrum master", "product owner", "product manager"
    ],
    "Analyste fonctionnel / Business Analyst": [
        "analyste fonctionnel", "business analyst", "analyste d'affaires"
    ],
    "Data": [
        "data scientist", "data engineer", "data analyst", "analyste données", "analyste data"
    ],
    "Administrateur systèmes": [
        "administrateur systèmes", "sysadmin", "ingénieur systèmes", "technicien systèmes"
    ],
    "Administrateur réseau": [
        "administrateur réseau", "network admin", "ingénieur réseau", "network engineer", "technicien réseau"
    ],
    "Technicien informatique / Support": [
        "technicien informatique", "support technique", "helpdesk", "service desk", "technicien support", "technicien maintenance", "analyste support", "technicien support applicatif"
    ],
    "Consultant IT": [
        "consultant IT", "consultant informatique", "consultant ERP", "consultant CRM"
    ],
    "Cybersécurité": [
        "sécurité informatique", "cybersécurité", "security analyst", "analyste sécurité", "pentester", "ethical hacker"
    ],
    "Administrateur base de données": [
        "administrateur base de données", "DBA", "database administrator"
    ],
    "Responsable informatique / Direction": [
        "responsable informatique", "directeur informatique", "CTO", "DSI"
    ],
    "Intégrateur": [
        "intégrateur", "intégrateur web"
    ],
    "Formateur IT": [
        "formateur informatique", "formateur IT"
    ]
}





domain_keywords = {
    "genie logiciel": [
        "développeur", "developpeur", "développeuse", "developpeuse", "développement", "developpement",
        "programmeur", "programmation", "software", "application", "dev", "fullstack", "backend", "frontend",
        "mobile", "android", "ios", "web", "api", "rest", "graphql", "microservices", "framework", "library", "coding"
    ],
    "reseau": [
        "réseau", "reseau", "network", "lan", "wan", "sd-wan", "wifi", "télécom", "telecom",
        "cisco", "switch", "routeur", "firewall", "vpn", "tcp/ip", "bgp", "ospf", "dns", "dhcp", "ethernet",
        "fibre", "optique", "networking", "routage", "cabling", "ipv4", "ipv6", "netflow"
    ],
    "infrastructure": [
        "infrastructure", "serveur", "server", "systeme", "système", "sysadmin", "admin système", 
        "virtualisation", "vmware", "hyper-v", "cloud", "azure", "aws", "gcp", "docker", "kubernetes",
        "linux", "unix", "windows server", "active directory", "backup", "restore", "storage", "san", "nas", "monitoring",
        "load balancer", "dns", "iis", "apache", "tomcat", "nginx"
    ],
    "cybersécurité": [
        "sécurité", "securite", "cybersécurité", "cybersecurite", "security", "soc", "pentest",
        "analyste sécurité", "hacking", "malware", "firewall", "antivirus", "authentification", "mfa",
        "ssl", "tls", "ipsec", "vpn", "sso", "iam", "zero trust", "owasp", "audit", "iso 27001", "gdpr", "compliance"
    ],
    "support": [
        "support", "technicien", "helpdesk", "service desk", "assistance", "soutien", "télémaintenance",
        "incident", "ticketing", "résolution", "hardware", "logiciel", "client", "utilisateur", "poste de travail",
        "windows", "mac", "linux", "formation utilisateur"
    ],
    "data": [
        "data", "données", "analyste données", "analyste data", "bi", "business intelligence", "big data",
        "data scientist", "data engineer", "etl", "power bi", "tableau", "qlik", "sql", "nosql", "hadoop", "spark",
        "airflow", "data lake", "data warehouse", "python", "pandas", "r", "statistique", "modélisation", "data mining"
    ],
    "intelligence artificielle": [
        "intelligence artificielle", "ia", "ai", "machine learning", "deep learning", "neural network",
        "réseaux de neurones", "tensorflow", "keras", "pytorch", "sklearn", "classification", "régression",
        "clustering", "nlp", "traitement du langage", "vision par ordinateur", "reconnaissance vocale", "gpt"
    ],
    "gestion de projet": [
        "chef de projet", "project manager", "gestion de projet", "scrum master", "agile", "scrum", "kanban",
        "pmo", "planning", "jira", "confluence", "trello", "asana", "méthodologie", "livrable", "budget",
        "ressources", "moa", "moi", "stakeholder"
    ],
    "base de données": [
        "base de données", "database", "sql", "pl/sql", "postgresql", "mysql", "mariadb", "sql server", "oracle",
        "mongodb", "nosql", "redis", "cassandra", "hbase", "indexation", "requête", "index", "jointure", "transaction",
        "optimisation", "dba", "backup bdd"
    ],
    "devops": [
        "devops", "ci/cd", "intégration continue", "déploiement", "docker", "kubernetes", "terraform",
        "ansible", "puppet", "chef", "jenkins", "gitlab-ci", "github actions", "monitoring", "observabilité",
        "grafana", "prometheus", "elk", "logstash", "scripting", "bash", "shell", "automation"
    ],
    "erp/crm": [
        "erp", "crm", "sap", "oracle erp", "sage", "dynamics", "salesforce", "navision", "odoo",
        "intégration erp", "gestion commerciale", "comptabilité", "facturation", "relation client", "modules erp"
    ],
    "qa/test": [
        "qa", "qualité", "test", "tester", "recette", "uat", "fonctionnel", "non-fonctionnel",
        "selenium", "cypress", "robot framework", "postman", "automatisation des tests", "test unitaire",
        "test d’intégration", "test de performance", "junit", "nunit", "coverage"
    ]
}
DOMAIN_CONFIGS = {
    "finance": {
        "skills": skills_finance,
        "domain_keywords": domain_keywords_finance,
        "job_categories": finance_job_categories,
        "url_template": 'https://www.jobboom.com/fr/autres-fonctions-en-finance/_i5m29lfr?sortBy=date&page={page}',
        "output_csv": "jobboom_finance.csv"
    },
    "it": {
        "skills": ALL_skills,
        "domain_keywords": domain_keywords,
        "job_categories": IT_job_categories,
        "url_template": 'https://www.jobboom.com/fr/technologies-medias-numeriques/_i10lfr?sortBy=date&page={page}',
        "output_csv": "jobboom_it.csv"
    }
}

def get_domaine_from_title(title, domain_name):
    if domain_name == "finance":
        return "finance"
    elif domain_name == "it":
        return "informatique"
    else:
        return "autre"


def extract_skills_from_list(description, skills_list):
    import re
    found_skills = set()
    desc_lower = description.lower()
    for skill in skills_list:
        skill_lower = skill.lower().strip()
        if not skill_lower:
            continue
        # Use word boundaries to match whole words only
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        if re.search(pattern, desc_lower):
            found_skills.add(skill)
    return " , ".join(sorted(found_skills))


def get_job_category(title):
    title_lower = title.lower()
    for category, keywords in finance_job_categories.items():
        for kw in keywords:
            if kw in title_lower:
                return category
    return "Autre"
def get_it_job_category(title):
    title_lower = title.lower()
    for category, keywords in IT_job_categories.items():
        for kw in keywords:
            if kw in title_lower:
                return category
    return "Autre"
def convert_relative_date(text):
    import re
    from datetime import datetime, timedelta

    mois_fr = {
        "janvier": "01", "février": "02", "mars": "03", "avril": "04",
        "mai": "05", "juin": "06", "juillet": "07", "août": "08",
        "septembre": "09", "octobre": "10", "novembre": "11", "décembre": "12"
    }

    text = text.lower().strip()
    today = datetime.today()

    if "aujourd'hui" in text:
        return today.strftime("%d-%m-%Y")
    elif "hier" in text:
        return (today - timedelta(days=1)).strftime("%d-%m-%Y")
    # il y a X jour(s)
    match = re.search(r"il y a\s*\+?\s*(\d+)\s*jour", text)
    if match:
        days_ago = int(match.group(1))
        return (today - timedelta(days=days_ago)).strftime("%d-%m-%Y")
    # il y a X semaine(s)
    match = re.search(r"il y a\s*\+?\s*(\d+)\s*semaine", text)
    if match:
        weeks_ago = int(match.group(1))
        return (today - timedelta(weeks=weeks_ago)).strftime("%d-%m-%Y")
    # il y a X heure(s)
    match = re.search(r"il y a\s*\+?\s*(\d+)\s*heure", text)
    if match:
        hours_ago = int(match.group(1))
        return (today - timedelta(hours=hours_ago)).strftime("%d-%m-%Y")
    # il y a X minute(s)
    match = re.search(r"il y a\s*\+?\s*(\d+)\s*minute", text)
    if match:
        minutes_ago = int(match.group(1))
        return (today - timedelta(minutes=minutes_ago)).strftime("%d-%m-%Y")
    # Ex: "12 juin 2024" ou "1 janvier 2023"
    match = re.search(r"(\d{1,2}) (\w+) (\d{4})", text)
    if match:
        day = match.group(1).zfill(2)
        month = mois_fr.get(match.group(2), "01")
        year = match.group(3)
        return f"{day}-{month}-{year}"
    # Ex: "12/06/2024" ou "12-06-2024"
    match = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", text)
    if match:
        day = match.group(1).zfill(2)
        month = match.group(2).zfill(2)
        year = match.group(3)
        return f"{day}-{month}-{year}"
    # Sinon, retourne la valeur brute
    return text

options = Options()
options.add_argument("--headless")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)

all_jobs = []

for domain_name, config in DOMAIN_CONFIGS.items():
    print(f"Scraping domain: {domain_name}")
    # Change the range below to scrape more pages if needed
    for page in range(1, 2):
        url = config["url_template"].format(page=page)
        driver.get(url)
        time.sleep(1)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_cards = soup.find_all('div', class_='job_item job_item_video')

        print(f"Page {page} ({domain_name}): {len(job_cards)} jobs trouvés")

        for card in job_cards:
            title_tag = card.find('p', class_='offre')
            a_tag = title_tag.find('a') if title_tag else None
            title = a_tag.text.strip() if a_tag else ""
            job_url = "https://www.jobboom.com" + a_tag['href'] if a_tag and 'href' in a_tag.attrs else ""

            location_tag = card.find('span', class_='jobCityProv')
            location = location_tag.text.strip() if location_tag else ""
            # Clean additional spaces and newlines in region/location
            import re
            location = re.sub(r'\s+', ' ', location).strip()

            sector_tag = card.find('span', class_='jobSector')
            sector = sector_tag.text.strip() if sector_tag else ""

            employer_tag = card.find('p', class_='employeur')
            company = employer_tag.find('span').text.strip() if employer_tag and employer_tag.find('span') else ""

            job_type = ""
            posted_date = ""
            skills_found = ""
            occupation = ""
            domaine = ""

            if job_url:
                try:
                    driver.get(job_url)
                    time.sleep(3)
                    job_soup = BeautifulSoup(driver.page_source, 'html.parser')
                    desc_tag = job_soup.find('div', id='job-content')

                    type_span = job_soup.find('span', class_='jobDescHeaderInfoSummaryItemText', attrs={"data-mdfga": "jobType"})
                    job_type = type_span.text.strip() if type_span else ""

                    if domain_name == "finance":
                        occupation = get_job_category(title)
                        domaine = get_domaine_from_title(title, domain_name)
                        skills_found = extract_skills_from_list(
                            desc_tag.get_text(separator='\n').strip() if desc_tag else "",
                            skills_finance
                        )
                    elif domain_name == "it":
                        occupation = get_it_job_category(title)
                        domaine = get_domaine_from_title(title, domain_name)
                        skills_found = extract_skills_from_list(
                            desc_tag.get_text(separator='\n').strip() if desc_tag else "",
                            ALL_skills
                        )


                    salary = ""
                    salary_blocks = job_soup.find_all('span', class_='jobDescHeaderInfoSummaryItem')
                    for block in salary_blocks:
                        svg = block.find('svg')
                        if svg and svg.find('use') and "#salary" in svg.find('use').get('xlink:href', ''):
                            salary_span = block.find('span', class_='jobDescHeaderInfoSummaryItemText')
                            if salary_span:
                                salary = salary_span.text.strip()
                                break

                    posted_span = job_soup.find('span', class_='jobDescHeaderJobPublishedStatus')
                    posted_date = posted_span.text.strip() if posted_span else ""
                    posted_date = convert_relative_date(posted_date)
                    if not desc_tag:
                        desc_tag = job_soup.find('div', class_='job_description')
                except Exception as e:
                    print(f"Erreur dans la page {job_url} : {e}")

            all_jobs.append((title, company, location, domaine, occupation, sector, job_type, salary, posted_date, job_url, skills_found, "Jobboom"))

driver.quit()

df = pd.DataFrame(
    all_jobs,
    columns=[
        "titre", "entreprise", "region", "domaine", "metier", "sector", "specialite", "salaire", "date_offre", "url", "competences", "source_site"
    ]
)
df = df.drop_duplicates()

# Reorder and select only the requested columns
df = df[[
    "titre",
    "date_offre",
    "entreprise",
    "region",
    "domaine",
    "specialite",
    "metier",
    "competences",
    "source_site",
    "url"
]]

print(df.head())
df.to_csv('joboom.csv', index=False, encoding='utf-8')