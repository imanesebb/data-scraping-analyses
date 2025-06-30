from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from competence_prediction_page import PredictionCompetencePage

class CompetenceDashboardPage(QtWidgets.QWidget):
    def __init__(self, df):
        super().__init__()
        self.df = df
        self.df = df.copy()
        self.df["COMPETENCE"] = self.df["COMPETENCE"].str.strip().str.lower()
        self.df["NOM_DOMAINE"] = self.df["NOM_DOMAINE"].str.strip()

        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)

        self.domain_combo = QtWidgets.QComboBox()
        self.domain_combo.addItems(["Informatique", "Finance"])

        self.period_combo = QtWidgets.QComboBox()
        self.period_combo.addItems(["Par Mois", "Par Année"])

        self.time_value_combo = QtWidgets.QComboBox()

        self.visualize_button = QtWidgets.QPushButton("Visualiser")
        self.visualize_button.clicked.connect(self.plot_competences)

        self.predict_button = QtWidgets.QPushButton("Voir la Prédiction")
        self.predict_button.clicked.connect(self.open_prediction_competence_window)

        self.save_button = QtWidgets.QPushButton("Enregistrer le Graphique")
        self.save_button.clicked.connect(self.save_graph)

        self.period_combo.currentIndexChanged.connect(self.update_time_values)
        self.domain_combo.currentIndexChanged.connect(self.update_time_values)

        self.update_time_values()

        control_layout = QtWidgets.QVBoxLayout()
        control_layout.setSpacing(20)
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

        control_widget = QtWidgets.QWidget()
        control_widget.setLayout(control_layout)
        control_widget.setFixedWidth(250)

        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.addWidget(control_widget)
        main_layout.addWidget(self.canvas, stretch=1)

    def update_time_values(self):
        self.time_value_combo.clear()
        period = self.period_combo.currentText()
        domaine = self.domain_combo.currentText()
        df_filtered = self.df[self.df["NOM_DOMAINE"] == domaine]
        if period == "Par Mois":
            values = sorted(df_filtered["MOIS"].dropna().unique())
        else:
            values = sorted(df_filtered["ANNEE"].dropna().unique())
        self.time_value_combo.addItem("")  # Master view
        self.time_value_combo.addItems([str(v) for v in values])

    def plot_competences(self):
        self.figure.clear()
        domaine = self.domain_combo.currentText()
        period = self.period_combo.currentText()
        selected_value = self.time_value_combo.currentText().strip()
        column = "MOIS" if period == "Par Mois" else "ANNEE"
        df_filtered = self.df[self.df["NOM_DOMAINE"] == domaine]

        if not selected_value:
            top_comp = (
                df_filtered[df_filtered["ANNEE"] == "2025"]
                .groupby("COMPETENCE")["NB_OFFRES"]
                .sum()
                .nlargest(5)
                .index.tolist()
            )

            df_top = df_filtered[df_filtered["COMPETENCE"].isin(top_comp)]
            df_grouped = df_top.groupby(["MOIS", "COMPETENCE"])["NB_OFFRES"].sum().reset_index()
            df_pivot = df_grouped.pivot(index="MOIS", columns="COMPETENCE", values="NB_OFFRES").fillna(0)
            ax = self.figure.add_subplot(111)
            df_pivot.plot(ax=ax, marker='o')
            ax.set_title(f"📈 Évolution des compétences - {domaine} (2025)")
            ax.set_xlabel("Mois")
            ax.set_ylabel("Nombre d'offres")
            ax.tick_params(axis='x', rotation=45)
            self.figure.tight_layout()
            self.canvas.draw()
            return

        df_filtered = df_filtered[df_filtered[column] == selected_value]
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
                ax.text(0.5, 0.5, "Aucune donnée", ha="center", va="center")
                ax.set_xticks([])
                ax.set_yticks([])
                continue

            top_comp = df_site.groupby("COMPETENCE")["NB_OFFRES"].sum().nlargest(3)
            top_comp.plot(kind="bar", ax=ax, color=color)
            ax.set_title(title)
            ax.set_ylabel("Offres")
            ax.set_xlabel("Compétence")
            ax.set_xticklabels(top_comp.index, rotation=45, ha="right")

        self.figure.tight_layout()
        self.canvas.draw()

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

    def open_prediction_competence_window(self):
        selected_domain = self.domain_combo.currentText()
        self.prediction_comp_window = PredictionCompetencePage(self.df, selected_domain)
        self.prediction_comp_window.show()
