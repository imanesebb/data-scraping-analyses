from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import pandas as pd
from prediction_page import PredictionPage  

class DomainDashboardPage(QtWidgets.QWidget):
    def __init__(self, df):
        super().__init__()
        self.df = df
        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)

        # UI elements
        self.domain_combo = QtWidgets.QComboBox()
        self.domain_combo.addItems(["Informatique", "Finance"])

        self.period_combo = QtWidgets.QComboBox()
        self.period_combo.addItems(["Par Mois", "Par Année"])

        self.time_value_combo = QtWidgets.QComboBox()

        self.visualize_button = QtWidgets.QPushButton("Visualiser")
        self.visualize_button.clicked.connect(self.plot_histograms)

        self.predict_button = QtWidgets.QPushButton("Voir la Prédiction")
        self.predict_button.clicked.connect(self.open_prediction_window)

        self.save_button = QtWidgets.QPushButton("Enregistrer le Graphique")
        self.save_button.clicked.connect(self.save_graph)

        self.period_combo.currentIndexChanged.connect(self.update_time_values)
        self.domain_combo.currentIndexChanged.connect(self.update_time_values)

        self.update_time_values()

        # Layout
        control_layout = QtWidgets.QVBoxLayout()
        control_layout.setSpacing(20)
        control_widget = QtWidgets.QWidget()
        control_widget.setLayout(control_layout)
        control_widget.setFixedWidth(250)

        control_layout.addWidget(QtWidgets.QLabel("📂 Domaine"))
        control_layout.addWidget(self.domain_combo)

        control_layout.addWidget(QtWidgets.QLabel("🗓️ Période"))
        control_layout.addWidget(self.period_combo)

        control_layout.addWidget(QtWidgets.QLabel("📅 Choix"))
        control_layout.addWidget(self.time_value_combo)

        control_layout.addWidget(self.visualize_button)
        control_layout.addWidget(self.predict_button)
        control_layout.addStretch()
        control_layout.addWidget(self.save_button)

        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.addWidget(control_widget)
        main_layout.addWidget(self.canvas, stretch=1)
    def save_graph(self):
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Enregistrer le graphique",
            "",
            "PNG Image (*.png);;PDF Document (*.pdf);;All Files (*)",
            options=options
        )

        if file_path:
            self.figure.savefig(file_path, bbox_inches='tight')
            QtWidgets.QMessageBox.information(
                self,
                "Succès",
                f"Graphique sauvegardé avec succès à:\n{file_path}"
            )

    def update_time_values(self):
        self.time_value_combo.clear()
        period = self.period_combo.currentText()
        domaine = self.domain_combo.currentText()

        df_filtered = self.df[self.df["NOM_DOMAINE"] == domaine]
        if period == "Par Mois":
            values = sorted(df_filtered["MOIS"].dropna().unique())
        else:
            values = sorted(df_filtered["ANNEE"].dropna().unique())

        self.time_value_combo.addItem("")  # 👑 Empty = Master plot
        self.time_value_combo.addItems([str(v) for v in values])

    def plot_histograms(self):
        domaine = self.domain_combo.currentText()
        period = self.period_combo.currentText()
        selected_value = self.time_value_combo.currentText().strip()

        column = "MOIS" if period == "Par Mois" else "ANNEE"
        df_filtered = self.df[self.df["NOM_DOMAINE"] == domaine]

        self.figure.clear()

        # 📈 MASTER PLOT if no value is selected
        if not selected_value:
            top_specialities = (
                df_filtered[df_filtered["ANNEE"] == "2025"]
                .groupby("NOM_SPECIALITE")["NOMBRE_OFFRES"]
                .sum()
                .sort_values(ascending=False)
                .head(5)
                .index.tolist()
            )

            df_time = df_filtered[df_filtered["NOM_SPECIALITE"].isin(top_specialities)]
            df_grouped = df_time.groupby(["MOIS", "NOM_SPECIALITE"])["NOMBRE_OFFRES"].sum().reset_index()

            df_pivot = df_grouped.pivot(index="MOIS", columns="NOM_SPECIALITE", values="NOMBRE_OFFRES").fillna(0)
            df_pivot = df_pivot.sort_index()

            ax = self.figure.add_subplot(111)
            df_pivot.plot(ax=ax, marker='o')

            ax.set_title(f"📈 Évolution des spécialités - {domaine} (2025)")
            ax.set_ylabel("Nombre d'offres")
            ax.set_xlabel("Mois")
            ax.tick_params(axis='x', rotation=45)  

            self.figure.tight_layout()
            self.canvas.draw()
            return


        # 🎯 Otherwise: histograms by SITE_TYPE
        df_filtered = df_filtered[df_filtered[column] == selected_value]

        if df_filtered.empty:
            QtWidgets.QMessageBox.information(
                self,
                "Aucune donnée",
                f"Aucune offre trouvée pour le domaine '{domaine}' en {selected_value}."
            )
            self.canvas.draw()
            return

        site_types = [
            ("Global", "#f4a261", "🟠 Global"),
            ("National", "#2a9d8f", "🔵 National"),
            ("International", "#e76f51", "🟢 International")
        ]

        for idx, (site, color, title) in enumerate(site_types, 1):
            ax = self.figure.add_subplot(1, 3, idx)
            df_site = df_filtered[df_filtered["SITE_TYPE"] == site]

            if df_site.empty:
                ax.set_title(title)
                ax.text(0.5, 0.5, "Aucune donnée", ha="center", va="center", fontsize=10)
                ax.set_xticks([])
                ax.set_yticks([])
                continue

            top3 = df_site.groupby("NOM_SPECIALITE")["NOMBRE_OFFRES"].sum().nlargest(3)
            top3.plot(kind="bar", ax=ax, color=color)
            ax.set_title(title)
            ax.set_ylabel("Offres")
            ax.set_xlabel("Spécialité")
            ax.set_xticklabels(top3.index, rotation=45, ha="right")

        self.figure.tight_layout()
        self.canvas.draw()

    def open_prediction_window(self):
        selected_domain = self.domain_combo.currentText()
        self.prediction_window = PredictionPage(self.df, selected_domain)
        self.prediction_window.show()




