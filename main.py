from PyQt5 import QtWidgets
from qt_material import apply_stylesheet
import pandas as pd
import sys

from dashboard_page import DomainDashboardPage
from competence_dashboard_page import CompetenceDashboardPage
from recommandation_page import RecommandationPage
from db_connection import get_connection
from data_loader import load_domain_data, load_competence_data, load_offre_competence_detail  

class MainApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard Analyse Emploi")
        self.resize(1300, 750)

        try:
            self.conn = get_connection()
            domain_df = load_domain_data(self.conn)
            competence_df = load_competence_data(self.conn)
            offres_comp_df = load_offre_competence_detail(self.conn) 
            competence_list = competence_df["COMPETENCE"].dropna().str.strip().str.lower().unique().tolist()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erreur Oracle", str(e))
            domain_df = pd.DataFrame()
            competence_df = pd.DataFrame()
            offres_comp_df = pd.DataFrame()
            competence_list = []

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                min-height: 40px;
                min-width: 400px;
                font-size: 12px;
                padding: 8px 20px;
            }
        """)
        self.tabs.addTab(DomainDashboardPage(domain_df), "📊 Specialité")
        self.tabs.addTab(CompetenceDashboardPage(competence_df), "🧠 Compétences")
        self.tabs.addTab(RecommandationPage(offres_comp_df, competence_list), "🎯 Recommandation")

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.tabs)

    def closeEvent(self, event):
        if hasattr(self, 'conn'):
            self.conn.close()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    apply_stylesheet(app, theme="light_blue.xml")
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
