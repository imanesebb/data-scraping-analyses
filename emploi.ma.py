"""
Scraper pour emploi.ma - Extraction des offres d'emploi (Informatique & Finance)
Avec modification pour forcer la région à "National" et colonnes spécifiques
"""
import logging 
import sys
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
from urllib.parse import urljoin, urlparse
import time

class EmploiMaScraper:
    def __init__(self):
        self.base_url = "https://www.emploi.ma"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.logger = logging.getLogger(__name__)
        
        # URLs de recherche pour Informatique et Finance uniquement
        self.search_urls = {
            "informatique": f"{self.base_url}/recherche-jobs-maroc?f%5B0%5D=im_field_offre_metiers:31",
            "finance": f"{self.base_url}/recherche-jobs-maroc?f%5B0%5D=im_field_offre_metiers:30"
        }
        
        self.all_jobs = []

    def clean_text(self, text):
        """Nettoie et normalise le texte"""
        if not text:
            return ""
        # Supprimer les espaces multiples et les caracteres speciaux
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'[^\w\s\-.,()/:@]', '', text)
        return text

    def extract_metier(self, title):
        """Extrait le metier principal depuis le titre du poste"""
        if not title:
            return "Autre"
        
        title_lower = title.lower()
        # Metiers specifiques a l'Informatique et Finance
        metiers = {
            # Informatique
            'developpeur': ['developpeur', 'developer', 'dev', 'programmeur'],
            'ingenieur': ['ingenieur', 'engineer', 'ing'],
            'architecte': ['architecte', 'architect'],
            'administrateur': ['administrateur', 'admin', 'administrator'],
            'analyste': ['analyste', 'analyst'],
            'chef de projet': ['chef de projet', 'project manager', 'charge de projet'],
            'consultant': ['consultant', 'conseiller'],
            'technicien': ['technicien', 'technician'],
            'designer': ['designer', 'graphiste', 'design'],
            'expert': ['expert', 'expertise'],
            'specialiste': ['specialiste', 'specialist'],
            
            # Finance
            'comptable': ['comptable', 'accounting'],
            'auditeur': ['auditeur', 'audit'],
            'controleur': ['controleur', 'controller'],
            'analyste financier': ['analyste financier', 'financial analyst'],
            'responsable': ['responsable', 'manager', 'head of'],
            'directeur': ['directeur', 'director', 'dir'],
            'tresorier': ['tresorier', 'treasurer'],
            'conseiller': ['conseiller', 'advisor'],
            'gestionnaire': ['gestionnaire', 'gestionnaire de'],
            'assistant': ['assistant', 'assistante']
        }
        
        for metier, variants in metiers.items():
            for variant in variants:
                if variant in title_lower:
                    return metier.title()
        
        return "Autre"

    def extract_specialite(self, title, description, domain):
        """Extrait la specialite depuis le titre et la description selon le domaine"""
        if not title:
            return "Generaliste"
        
        combined_text = f"{title} {description}".lower()
        
        # Specialites par domaine
        if domain == "informatique":
            specialites_it = {
                'developpement web': [
                    'web', 'frontend', 'backend', 'fullstack', 'html', 'css', 'javascript',
                    'react', 'angular', 'vue', 'php', 'laravel', 'symfony', 'typescript',
                    'node.js', 'express', 'django', 'asp.net', 'bootstrap', 'tailwind'
                ],
                'developpement mobile': [
                    'mobile', 'android', 'ios', 'react native', 'flutter', 'swift', 'kotlin',
                    'xamarin', 'cordova', 'ionic', 'mobile app'
                ],
                'data science': [
                    'data', 'big data', 'machine learning', 'deep learning', 'ai',
                    'intelligence artificielle', 'nlp', 'tensorflow', 'pytorch', 'python',
                    'r', 'spark', 'pandas', 'scikit-learn', 'data engineer', 'data analyst'
                ],
                'cybersecurite': [
                    'securite', 'cybersecurite', 'security', 'firewall', 'pentest',
                    'ethical hacking', 'kali', 'vpn', 'tls', 'owasp', 'zero trust', 'soc'
                ],
                'devops': [
                    'devops', 'docker', 'kubernetes', 'ci/cd', 'jenkins', 'ansible',
                    'terraform', 'gitlab ci', 'helm', 'prometheus', 'grafana'
                ],
                'cloud': [
                    'cloud', 'aws', 'azure', 'gcp', 'google cloud', 'ec2', 's3',
                    'lambda', 'cloudformation', 'serverless', 'cloud engineer'
                ],
                'base de donnees': [
                    'database', 'dba', 'sql', 'mysql', 'postgresql', 'oracle', 'nosql',
                    'mongodb', 'cassandra', 'redis', 'clickhouse', 'firebase'
                ],
                'reseau': [
                    'reseau', 'network', 'cisco', 'infrastructure', 'tcp/ip', 'vpn', 'dns',
                    'lan', 'wan', 'ipv4', 'ipv6', 'routing', 'switch'
                ],
                'erp/crm': [
                    'erp', 'crm', 'sap', 'odoo', 'salesforce', 'sage', 'oracle erp',
                    'ms dynamics', 'hubspot', 'zoho', 'netsuite'
                ],
                'business intelligence': [
                    'bi', 'power bi', 'tableau', 'qlik', 'dataviz', 'datastudio', 'etl',
                    'ssrs', 'ssis', 'data warehouse'
                ],
                'systeme': [
                    'systeme', 'system', 'linux', 'windows', 'unix', 'sysadmin', 'vmware',
                    'bash', 'powershell', 'hyper-v'
                ],
                'qualite logiciel': [
                    'qa', 'test', 'testing', 'automatisation', 'selenium', 'cypress',
                    'postman', 'jmeter', 'bug', 'test automation', 'tdd', 'bdd'
                ]
            }

            for specialite, keywords in specialites_it.items():
                for keyword in keywords:
                    if keyword in combined_text:
                        return specialite.title()

        elif domain == "finance":
            specialites_finance = {
                'comptabilite generale': [
                    'comptabilite', 'accounting', 'comptable', 'journal', 'grand livre',
                    'balance', 'saisie', 'facturation', 'ecriture comptable'
                ],
                'audit': [
                    'audit', 'auditeur', 'audit interne', 'audit externe', 'conformite',
                    'controle qualite', 'audit financier', 'norme ISO'
                ],
                'controle de gestion': [
                    'controle de gestion', 'controlling', 'budget', 'analyse budgetaire',
                    'kpi', 'previsionnel', 'forecast', 'indicateurs'
                ],
                "finance d'entreprise": [
                    'finance', 'financier', 'tresorerie', 'cash flow', 'analyse bilancielle',
                    'liquidite', 'fonds de roulement', 'analyse financiere'
                ],
                'banque': [
                    'banque', 'banking', 'credit', 'pret', 'compte bancaire',
                    'services bancaires', 'taux interet', 'epargne'
                ],
                'assurance': [
                    'assurance', 'contrat assurance', 'sinistre', 'indemnisation',
                    'actuaire', 'prime', 'courtage'
                ],
                'fiscalite': [
                    'fiscalite', 'impot', 'tva', 'is', 'ir', 'declaration fiscale',
                    'optimisation fiscale', 'controle fiscal'
                ],
                'investissement': [
                    'investissement', 'investment', 'portefeuille', 'analyse de portefeuille',
                    'gestion actifs', 'private equity', 'actions', 'obligations'
                ],
                'risk management': [
                    'risque', 'risk', 'gestion des risques', 'risk management', 'KYC',
                    'AML', 'fraude', 'solvabilite', 'Bale'
                ],
                'consolidation': [
                    'consolidation', 'ifrs', 'reporting', 'etats financiers', 'multi-entite',
                    'comptes consolides', 'interco'
                ],
                'paie': [
                    'paie', 'payroll', 'salaire', 'bulletin de paie', 'cotisation',
                    'charges sociales', 'declaration cnss'
                ],
                'credit': [
                    'credit', 'loan', 'financement', 'analyse de credit',
                    'score de credit', 'taux', 'leasing'
                ],
                'tresorerie': [
                    'tresorerie', 'cash management', 'prevision de tresorerie',
                    'flux de tresorerie', 'liquidite', 'banque'
                ],
                'marches financiers': [
                    'marches financiers', 'trading', 'bourse', 'forex', 'derives',
                    'produits financiers', 'actions', 'obligations'
                ],
                'analyse financiere': [
                    'analyse financiere', 'ratios financiers', 'rentabilite',
                    'compte de resultat', 'bilan', 'marge brute', 'ebitda'
                ]
            }

            for specialite, keywords in specialites_finance.items():
                for keyword in keywords:
                    if keyword in combined_text:
                        return specialite.title()

        return "Generaliste"

    def extract_job_details(self, job_element):
        """Extrait les details specifiques d'une offre d'emploi"""
        try:
            job_data = {}
        
            # Titre du poste
            title_elem = job_element.select_one('h3 a, .job-title a, .card-title a')
            if title_elem:
                raw_title = self.clean_text(title_elem.get_text())
                # Supprimer les noms de villes du titre
                morocco_cities = [
                    'casablanca', 'rabat', 'marrakech', 'fes', 'tanger', 'agadir', 'meknes', 
                    'oujda', 'kenitra', 'tetouan', 'safi', 'mohammedia', 'khouribga',
                    'beni mellal', 'el jadida', 'nador', 'settat', 'berrechid'
                ]
                
                clean_title = raw_title
                for city in morocco_cities:
                    # Supprimer la ville avec differents patterns
                    patterns = [
                        rf'\b{city}\b',  # Ville seule
                        rf'- {city}',    # Avec tiret
                        rf'$${city}$$',  # Entre parentheses
                        rf', {city}',    # Avec virgule
                        rf' {city}$',    # En fin de titre
                        rf'^{city} -',   # Au debut avec tiret
                    ]
                    for pattern in patterns:
                        clean_title = re.sub(pattern, '', clean_title, flags=re.IGNORECASE)
                
                # Nettoyer les espaces multiples et tirets en trop
                clean_title = re.sub(r'\s*-\s*$', '', clean_title)  # Tiret en fin
                clean_title = re.sub(r'^\s*-\s*', '', clean_title)  # Tiret au debut
                clean_title = re.sub(r'\s+', ' ', clean_title).strip()
                
                job_data['titre'] = clean_title
            else:
                job_data['titre'] = ""
        
            # URL de l'offre
            job_data['url'] = urljoin(self.base_url, title_elem.get('href')) if title_elem else ""
        
            # Entreprise
            company_elem = job_element.select_one('a.card-job-company, .company-name, .card-job-company-name')
            job_data['entreprise'] = self.clean_text(company_elem.get_text()) if company_elem else ""
        
            # Region/Localisation - Toujours "National"
            job_data['region'] = "National"
        
            # Competence - extraction depuis la description
            desc_elem = job_element.select_one('div.card-job-description, .job-description, .description')
            competence_list = []
            description_text = ""
            
            if desc_elem:
                description_text = desc_elem.get_text().lower()
            
                # Competences specifiques IT et Finance
                it_competence = [
                    'python', 'java', 'javascript', 'typescript', 'php', 'c++', 'c#', 'go', 'ruby', 'swift', 'kotlin',
                    'sql', 'mysql', 'postgresql', 'oracle', 'mariadb', 'sqlite', 'nosql', 'mongodb', 'cassandra', 'redis',
                    'html', 'css', 'scss', 'less', 'bootstrap', 'tailwind', 
                    'react', 'angular', 'vue', 'svelte', 'next.js', 'nuxt.js',
                    'node.js', 'express', 'django', 'flask', 'spring', 'laravel', 'symfony', 'asp.net', 'dotnet',
                    'git', 'github', 'gitlab', 'bitbucket', 'svn',
                    'docker', 'kubernetes', 'jenkins', 'ansible', 'puppet', 'terraform', 'vagrant',
                    'aws', 'azure', 'gcp', 'google cloud', 'cloudflare', 'cloudformation', 'lambda', 'firebase',
                    'linux', 'ubuntu', 'centos', 'redhat', 'debian', 'windows', 'unix', 'bash', 'powershell',
                    'elasticsearch', 'kibana', 'logstash', 'splunk', 'prometheus', 'grafana',
                    'jira', 'confluence', 'postman', 'cypress', 'selenium', 'playwright', 'jmeter',
                    'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'hadoop', 'spark', 'airflow', 'mlflow'
                ]

                finance_competence = [
                    'excel', 'advanced excel', 'macros', 'vba', 'power query',
                    'sap', 'sap fi', 'sap mm', 'sap fico', 'sap hana',
                    'sage', 'sage 100', 'sage x3',
                    'quickbooks', 'xero', 'wave accounting', 'odoo',
                    'ifrs', 'gaap', 'ias', 'budgeting', 'forecasting',
                    'bloomberg', 'reuters', 'factset',
                    'power bi', 'tableau', 'qlikview', 'dataviz',
                    'audit', 'audit interne', 'audit externe', 'internal controls', 'sox',
                    'consolidation', 'reporting financier', 'etats financiers', 'bilan',
                    'risk management', 'gestion des risques', 'compliance', 'aml', 'kyc',
                    'treasury', 'tresorerie', 'cash flow', 'cash management',
                    'cost accounting', 'controle de gestion', 'analyse des couts',
                    'tax', 'taxation', 'tva', 'impot', 'declaration fiscale',
                    'finance entreprise', 'analyse financiere', 'ratios financiers', 'marge', 'ebitda',
                    'erp', 'oracle erp', 'dynamics 365', 'netsuite', 'crm finance'
                ]

                all_competence = it_competence + finance_competence
            
                for competence in all_competence:
                    if competence in description_text:
                        competence_list.append(competence.title())
        
            job_data['competences'] = ', '.join(competence_list) if competence_list else ""
        
            # Domaine (sera rempli dans scrape_page)
            job_data['domaine'] = ""

            # Metier - extraction depuis le titre
            metier = self.extract_metier(job_data['titre'])
            job_data['metier'] = metier

            # Specialite - sera remplie dans scrape_page avec le domaine
            job_data['specialite'] = ""
        
            # Date de l'offre
            date_elem = None
            date_selectors = [
                '.date', '.published-date', '.job-date', 
                '[class*="date"]', '.card-job-date',
                'time', '[datetime]', '.publication-date'
            ]

            for selector in date_selectors:
                date_elem = job_element.select_one(selector)
                if date_elem:
                    break

            if date_elem:
                date_text = self.clean_text(date_elem.get_text())
                # Nettoyer le texte de date
                date_text = re.sub(r'^(Publie|Published|Date):\s*', '', date_text, flags=re.IGNORECASE)
                # Try to parse and format the date
                date_formats = [
                    "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d"
                ]
                parsed_date = None
                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(date_text, fmt)
                        break
                    except Exception:
                        continue
                if parsed_date:
                    job_data['date_offre'] = parsed_date.strftime("%d-%m-%Y")
                else:
                    job_data['date_offre'] = date_text
            else:
                # Essayer d'extraire la date depuis les attributs HTML
                datetime_elem = job_element.select_one('[datetime]')
                if datetime_elem:
                    raw_date = datetime_elem.get('datetime', '')
                    parsed_date = None
                    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%d-%m-%Y"):
                        try:
                            parsed_date = datetime.strptime(raw_date, fmt)
                            break
                        except Exception:
                            continue
                    if parsed_date:
                        job_data['date_offre'] = parsed_date.strftime("%d-%m-%Y")
                    else:
                        job_data['date_offre'] = raw_date
                else:
                    # Chercher dans tout le texte de l'element job
                    full_text = job_element.get_text()
                    date_patterns = [
                        r'il y a \d+ jour[s]?',
                        r'il y a \d+ heure[s]?',
                        r'il y a \d+ semaine[s]?',
                        r'\d{1,2}/\d{1,2}/\d{4}',
                        r'\d{1,2}-\d{1,2}-\d{4}',
                        r'Publie le \d{1,2}/\d{1,2}/\d{4}'
                    ]
                    
                    date_found = ""
                    for pattern in date_patterns:
                        match = re.search(pattern, full_text, re.IGNORECASE)
                        if match:
                            date_found = match.group()
                            # Try to extract and format the date
                            date_match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', date_found)
                            if date_match:
                                try:
                                    parsed_date = datetime.strptime(date_match.group(), "%d/%m/%Y")
                                except Exception:
                                    try:
                                        parsed_date = datetime.strptime(date_match.group(), "%d-%m-%Y")
                                    except Exception:
                                        parsed_date = None
                                if parsed_date:
                                    date_found = parsed_date.strftime("%d-%m-%Y")
                            break
                    job_data['date_offre'] = date_found
        
            # Source du site
            job_data['source_site'] = "emploi.ma"
            
            # Stocker la description pour l'extraction de specialite
            job_data['_description'] = description_text
        
            return job_data
        
        except Exception as e:
            self.logger.error(f"Erreur lors de l'extraction des details du job: {e}")
            return None

    def scrape_page(self, url, domain_name):
        """Scrape une page de resultats"""
        try:
            self.logger.info(f"📄 Scraping: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Selecteurs pour les offres d'emploi
            job_elements = soup.select('div.card.card-job')
            
            if not job_elements:
                # Essayer d'autres selecteurs
                job_elements = soup.select('div.card, .job-item, .offer-item')
            
            self.logger.info(f"   Trouve {len(job_elements)} offres sur cette page")
            
            page_jobs = []
            for job_elem in job_elements:
                job_data = self.extract_job_details(job_elem)
                if job_data:
                    job_data['domaine'] = domain_name.title()
                    # Extraire la specialite avec le domaine
                    job_data['specialite'] = self.extract_specialite(
                        job_data['titre'], 
                        job_data.get('_description', ''), 
                        domain_name
                    )
                    # Supprimer la description temporaire
                    if '_description' in job_data:
                        del job_data['_description']
                    page_jobs.append(job_data)
            
            return page_jobs
            
        except requests.RequestException as e:
            self.logger.error(f"Erreur de requete pour {url}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Erreur lors du scraping de {url}: {e}")
            return []

    def scrape_domain(self, domain_name, max_pages=20, max_jobs_remaining=None):
        """Scrape toutes les pages d'un domaine"""
        if domain_name not in self.search_urls:
            return []

        base_url = self.search_urls[domain_name]
        domain_jobs = []

        for page in range(1, max_pages + 1):  # <-- Fix here
            if max_jobs_remaining and len(domain_jobs) >= max_jobs_remaining:
                break

            page_url = base_url if page == 1 else f"{base_url}&page={page}"
            page_jobs = self.scrape_page(page_url, domain_name)

            if not page_jobs:
                break

            if max_jobs_remaining:
                remaining_space = max_jobs_remaining - len(domain_jobs)
                if remaining_space > 0:
                    page_jobs = page_jobs[:remaining_space]

            domain_jobs.extend(page_jobs)

            # ✅ Affichage simple dans le terminal
            print(f"Page {page}")

            time.sleep(2)

        return domain_jobs

    def scrape_all_domains(self, domains=None, max_pages=20, max_jobs=100):
        """Scrape tous les domaines specifies (Informatique et Finance)"""
        if domains is None:
            domains = ['informatique', 'finance']  # Par defaut, les deux domaines
        
        self.logger.info(f"🚀 Debut du scraping pour les domaines: {[d.upper() for d in domains]}")
        if max_jobs:
            self.logger.info(f"   Limite maximum: {max_jobs} offres")
        else:
            self.logger.info("   SCRAPING COMPLET - TOUTES LES OFFRES DISPONIBLES")
        
        for domain in domains:
            if domain in self.search_urls:
                # Verifier si on a deja atteint la limite (seulement si une limite est definie)
                if max_jobs and len(self.all_jobs) >= max_jobs:
                    self.logger.info(f"Limite de {max_jobs} offres atteinte, arret du scraping")
                    break
                
                # Calculer combien d'offres on peut encore recuperer
                remaining_jobs = None
                if max_jobs:
                    remaining_jobs = max_jobs - len(self.all_jobs)
                
                domain_jobs = self.scrape_domain(domain, max_pages, remaining_jobs)
                self.all_jobs.extend(domain_jobs)
                
                # Pause entre les domaines
                time.sleep(2)
            else:
                self.logger.warning(f"Domaine ignore (non supporte): {domain}")
        
        # Limiter a max_jobs seulement si une limite est definie
        if max_jobs and len(self.all_jobs) > max_jobs:
            self.all_jobs = self.all_jobs[:max_jobs]
            self.logger.info(f"Donnees tronquees a {max_jobs} offres")
        
        self.logger.info(f"🎉 Scraping termine. Total: {len(self.all_jobs)} offres recuperees")
        return self.all_jobs

    def save_to_csv(self, filename=None, max_rows=None):
        """Sauvegarde les donnees filtrees dans un fichier CSV avec les colonnes specifiees"""
        if not self.all_jobs:
            self.logger.warning("Aucune donnee a sauvegarder")
            return None

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"emploi_ma_IT_Finance_{timestamp}.csv"

        try:
            # Creer le DataFrame avec les colonnes specifiees
            df = pd.DataFrame(self.all_jobs)

            # Colonnes requises dans l'ordre specifie
            required_columns = [
                'titre', 'date_offre', 'entreprise', 'region',
                'domaine', 'specialite', 'metier', 'competences',
                'source_site', 'url'
            ]

            # S'assurer que toutes les colonnes existent
            for col in required_columns:
                if col not in df.columns:
                    df[col] = ""

            # Selectionner uniquement les colonnes requises dans l'ordre demande
            df = df[required_columns]

            # Nettoyer et filtrer les donnees
            df = df.drop_duplicates(subset=['titre', 'entreprise'], keep='first')
            df = df.dropna(subset=['titre'])
            df = df[df['titre'].str.len() > 0]

            # Forcer la region a "National" pour toutes les lignes
            df['region'] = "National"

            # Filtrer les offres avec au moins une information utile
            df = df[
                (df['entreprise'].str.len() > 0) | 
                (df['competences'].str.len() > 0)
            ]

            # --- AJOUT : Forcer le format de date_offre ---
            def format_date(date_str):
                for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%Y/%m/%d", "%d.%m.%Y"):
                    try:
                        return datetime.strptime(str(date_str), fmt).strftime("%d-%m-%Y")
                    except Exception:
                        continue
                return date_str  # Si parsing echoue, garder la valeur originale

            df['date_offre'] = df['date_offre'].apply(format_date)
            # --- FIN AJOUT ---

            # LIMITER SEULEMENT SI max_rows EST DEFINI
            if max_rows and len(df) > max_rows:
                df = df.head(max_rows)
                self.logger.info(f"Donnees limitees a {max_rows} lignes comme demande")
            else:
                self.logger.info(f"💾 SAUVEGARDE COMPLETE: {len(df)} offres")

            # Sauvegarder
            df.to_csv(filename, index=False, encoding='utf-8-sig')

            self.logger.info(f"✅ Donnees IT & Finance sauvegardees dans {filename}")
            self.logger.info(f"📊 Nombre de lignes dans le CSV: {len(df)}")

            return filename

        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde: {e}")
            return None

    def get_statistics(self):
        """Retourne des statistiques sur les donnees scrapees"""
        if not self.all_jobs:
            return {}
        
        df = pd.DataFrame(self.all_jobs)
        
        stats = {
            'total_jobs': len(df),
            'unique_companies': df['entreprise'].nunique(),
            'domains': df['domaine'].value_counts().to_dict(),
            'metiers': df['metier'].value_counts().head(10).to_dict(),
            'specialites': df['specialite'].value_counts().head(10).to_dict()
        }
        
        return stats

def setup_logging():
    """Configuration du logging"""
    import os
    import logging
    from datetime import datetime

    if not os.path.exists('logs'):
        os.makedirs('logs')

    log_filename = f"logs/scraping_IT_Finance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8')
        ]
    )
    return log_filename

def main():
    """Script principal pour lancer le scraping et sauvegarder le CSV"""
    log_file = setup_logging()
    logger = logging.getLogger(__name__)

    try:
        scraper = EmploiMaScraper()
        domains = ['informatique', 'finance']
        max_pages = 20
        max_jobs=None

        jobs = scraper.scrape_all_domains(domains, max_pages=max_pages, max_jobs=max_jobs)

        if not jobs:
            print("❌ Aucune offre récupérée.")
            return

        csv_path = "emploima.csv"
        scraper.save_to_csv(filename=csv_path)

        print("✅ Scraping terminé avec succès.")
        print(f"📄 Fichier CSV : {os.path.abspath(csv_path)}")

    except KeyboardInterrupt:
        print("⛔ Scraping interrompu par l'utilisateur.")
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main()

print("✅ Scraper EmploiMa (IT & Finance) initialise avec succes!")