# 🧠 Job Market Intelligence Dashboard (Morocco + International)

This project is a Python-based **job analysis and prediction dashboard** designed to:
- Scrape and store job listings from Moroccan and international websites
- Analyze job offer trends by domain, specialty, region, and month
- Predict job market evolution using **XGBoost** + **scikit-learn**
- Match uploaded CVs to the most compatible job offers using NLP and SQL
- Provide a modern, interactive dashboard with **PyQt5** and **matplotlib**

---

## 🎯 Features

### ✅ Data Ingestion
- Web scraping from websites like `emploi.ma`, `marocannonces.com`, and international sources
- Structured storage in a fully relational **Oracle** database

### ✅ Data Analysis
- Interactive dashboard to explore:
  - Offers per domain/specialty
  - Trends over months/years
  - Region-level breakdowns
  - National vs International stats

### ✅ Job Prediction
- Predicts job offer volume from **June 2025 to Jan 2026**
- Uses **XGBoost regressors** wrapped in a **scikit-learn pipeline**
- Visualized via side-by-side bar plots

### ✅ CV Matching
- Upload a **PDF CV**
- Extracts text and compares with job requirements (`COMPETENCE` table)
- Returns top 10 job offers best matching the CV (based on skill overlap)

---

## 🛠️ Tech Stack

| Category         | Tools / Libraries                           |
|------------------|---------------------------------------------|
| Language         | Python 3.x                                  |
| GUI              | PyQt5, qt-material                          |
| Data Analysis    | pandas, matplotlib                          |
| ML/Prediction    | scikit-learn, xgboost                       |
| PDF Parsing      | pdfminer.six                                |
| DBMS             | Oracle (SQL Developer / Oracle XE)          |
| Scraping         | BeautifulSoup, Requests, Selenium (option) |

---

## 🗂️ Project Structure
├── main.py # Launches the dashboard
├── db_connection.py # Oracle DB connector
├── data_loader.py # Loads cleaned data from SQL
├── dashboard_page.py # Domain analysis view
├── prediction_page.py # XGBoost-based prediction
├── job_matcher_page.py # CV upload + top 10 job match
├── job_matcher_logic.py # Text extraction + SQL matching logic
├── /scrapcode/ # Job scraper scripts
└── /DATABASE/ # Database creation scripts and csv insertions

### 🔧 1. Install Requirements

pandas
numpy
matplotlib
PyQt5
qt-material
pdfminer.six
xgboost
scikit-learn
oracledb



