from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import pandas as pd
import os

from job_matcher import extract_text_from_pdf, match_jobs
from db_connection import get_connection

class MatplotlibWindow(QtWidgets.QWidget):
    def __init__(self, df_scores, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Graphique des correspondances")
        self.resize(800, 600)
        layout = QtWidgets.QVBoxLayout(self)

        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.plot_scores(df_scores)

    def plot_scores(self, df_scores):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        # On trace le score en fonction du titre de l'offre
        df_scores.plot(kind="barh", y="score", x="titre", ax=ax, color="#2a9d8f")
        ax.set_xlabel("Score de correspondance (%)")
        ax.set_ylabel("Titre de l'offre")
        ax.set_title("🔍 Score des meilleures correspondances")
        self.figure.tight_layout()
        self.canvas.draw()

class RecommandationPage(QtWidgets.QWidget):
    def __init__(self, df_offres, competence_list):
        super().__init__()
        self.df_offres = df_offres
        self.competence_list = [c.lower() for c in competence_list]

        self.setWindowTitle("🔎 Recommandation d'offres à partir du CV")
        self.resize(900, 600)

        layout = QtWidgets.QVBoxLayout(self)

        self.upload_button = QtWidgets.QPushButton("📄 Charger le CV (.pdf)")
        self.upload_button.clicked.connect(self.browse_and_match_cv)
        layout.addWidget(self.upload_button)

        self.result_label = QtWidgets.QLabel("Aucune recommandation disponible.")
        layout.addWidget(self.result_label)

        self.table = QtWidgets.QTableWidget()
        layout.addWidget(self.table)

        self.graph_window = None  # Référence à la fenêtre graphique

    def browse_and_match_cv(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Sélectionnez votre CV (PDF)",
            "",
            "PDF files (*.pdf)"
        )
        if file_path:
            try:
                cv_text = extract_text_from_pdf(file_path)
            except RuntimeError as e:
                QtWidgets.QMessageBox.critical(self, "Erreur PDF", str(e))
                return

            conn = get_connection()
            matches_df = match_jobs(cv_text, conn)
            conn.close()

            self.show_cv_matches(matches_df)

    def show_cv_matches(self, matches_df):
        top_matches = matches_df.head(10)

        if top_matches.empty:
            self.result_label.setText("Aucune offre correspondante trouvée.")
            self.table.clearContents()
            self.table.setRowCount(0)
            if self.graph_window:
                self.graph_window.close()
            return

        self.result_label.setText(f"Top {len(top_matches)} offres correspondant à votre CV:")

        # Remplir la table
        self.table.clearContents()
        self.table.setRowCount(len(top_matches))
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Titre", "Entreprise", "Domaine", "Spécialité", "Score (%)", "ID Offre"])

        for i, (_, row) in enumerate(top_matches.iterrows()):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(row.titre)))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(row.entreprise)))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(str(row.nom_domaine)))
            self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(row.nom_specialite)))
            self.table.setItem(i, 4, QtWidgets.QTableWidgetItem(f"{row.score:.1f}"))
            self.table.setItem(i, 5, QtWidgets.QTableWidgetItem(str(row.id_offre)))

        self.table.resizeColumnsToContents()

        # Afficher le graphique dans une fenêtre séparée
        if self.graph_window is not None:
            self.graph_window.close()  # Fermer l'ancienne fenêtre si ouverte

        self.graph_window = MatplotlibWindow(top_matches)
        self.graph_window.show()
