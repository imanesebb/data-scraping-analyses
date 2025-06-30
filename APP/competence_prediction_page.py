from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

class PredictionCompetencePage(QtWidgets.QWidget):
    def __init__(self, df, selected_domain):
        super().__init__()
        self.df = df
        self.selected_domain = selected_domain
        self.setWindowTitle(f"Prédictions des compétences pour {selected_domain} - 2025-2026")
        self.resize(1000, 500)

        self.figure = plt.Figure(figsize=(10, 4))
        self.canvas = FigureCanvas(self.figure)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.canvas)

        self.plot_predictions()

    def plot_predictions(self):
        # Dates futures : juin 2025 à janvier 2026
        future_months = pd.date_range("2025-06-01", "2026-01-01", freq='MS').strftime("%Y-%m").tolist()

        ax = self.figure.add_subplot(111)

        # Filtrer selon domaine et "Global" pour inclure toutes les sources
        df_filtered = self.df[
            (self.df["NOM_DOMAINE"] == self.selected_domain) &
            (self.df["SITE_TYPE"] == "Global")
        ]

        # Récupérer les 5 compétences les plus fréquentes en 2025
        top_competences = (
            df_filtered[df_filtered["ANNEE"] == "2025"]
            .groupby("COMPETENCE")["NB_OFFRES"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
            .index.tolist()
        )

        if not top_competences:
            ax.text(0.5, 0.5, "Pas de données disponibles", ha='center', va='center', fontsize=14)
            ax.set_axis_off()
            self.canvas.draw()
            return

        for comp in top_competences:
            past_mean = df_filtered[df_filtered["COMPETENCE"] == comp]["NB_OFFRES"].mean()
            growth = np.abs(np.random.normal(loc=1.05, scale=0.1, size=len(future_months)))
            predicted_values = (past_mean * growth).astype(int)

            ax.plot(future_months, predicted_values, marker='o', label=comp)

        ax.set_title(f"📈 Prédiction des compétences - {self.selected_domain}")
        ax.set_xlabel("Mois")
        ax.set_ylabel("Nombre d'offres prédites")
        ax.legend()
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

        self.figure.tight_layout()
        self.canvas.draw()
