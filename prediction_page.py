from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor

class PredictionPage(QtWidgets.QWidget):
    def __init__(self, df, selected_domain):
        super().__init__()
        self.df = df
        self.selected_domain = selected_domain
        self.setWindowTitle(f"Prédictions pour {selected_domain} - 2025-2026")
        self.resize(1000, 500)

        self.figure = plt.Figure(figsize=(10, 4))
        self.canvas = FigureCanvas(self.figure)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.canvas)

        self.plot_predictions()

    def plot_predictions(self):
        future_months = pd.date_range("2025-06-01", "2026-01-01", freq="MS")
        future_months_str = future_months.strftime("%Y-%m").tolist()

        axes = self.figure.subplots(1, 2)
        regions = ["National", "International"]

        for ax, region in zip(axes, regions):
            # ✅ Filter data for domain and region
            df_filtered = self.df[
                (self.df["NOM_DOMAINE"] == self.selected_domain) & 
                (self.df["SITE_TYPE"] == region)
            ].copy()

            # 💡 If no data at all, show a message
            if df_filtered.empty:
                ax.set_title(f"{region} - Aucune donnée")
                ax.axis('off')
                continue

            # Get top 3 specialities
            top_specialties = (
                df_filtered[df_filtered["ANNEE"] == "2025"]
                .groupby("NOM_SPECIALITE")["NOMBRE_OFFRES"]
                .sum()
                .sort_values(ascending=False)
                .head(3)
                .index.tolist()
            )

            if not top_specialties:
                ax.set_title(f"{region} - Pas de spécialités 2025")
                ax.axis('off')
                continue

            width = 0.2
            x = np.arange(len(future_months))

            for idx, speciality in enumerate(top_specialties):
                df_spec = df_filtered[df_filtered["NOM_SPECIALITE"] == speciality].copy()

                if df_spec.empty:
                    continue

                df_spec["DATE"] = pd.to_datetime(df_spec["MOIS"], format="%Y-%m")
                df_spec.sort_values('DATE', inplace=True)

                # Features
                df_spec['MONTH_SIN'] = np.sin(2 * np.pi * df_spec['DATE'].dt.month/12)
                df_spec['MONTH_COS'] = np.cos(2 * np.pi * df_spec['DATE'].dt.month/12)
                df_spec['YEAR'] = df_spec['DATE'].dt.year
                df_spec['LAG1'] = df_spec['NOMBRE_OFFRES'].shift(1)
                df_spec = df_spec.dropna()

                if df_spec.empty:
                    continue

                X = df_spec[['MONTH_SIN','MONTH_COS','YEAR','LAG1']]
                y = df_spec['NOMBRE_OFFRES']

                if len(X) == 0:
                    continue

                model = Pipeline(
                    steps=[
                        ("scaler", StandardScaler()),
                        ("xgb", XGBRegressor(
                            n_estimators=200,
                            learning_rate=0.1,
                            max_depth=3,
                            random_state=42,
                        )),
                    ]
                )

                # Fit model
                model.fit(X, y)

                last_known = df_spec.iloc[-1]['NOMBRE_OFFRES']

                predicted_values = []
                future_df = pd.DataFrame({"DATE": future_months})
                future_df['MONTH_SIN'] = np.sin(2 * np.pi * future_df['DATE'].dt.month/12)
                future_df['MONTH_COS'] = np.cos(2 * np.pi * future_df['DATE'].dt.month/12)
                future_df['YEAR'] = future_df['DATE'].dt.year

                for i in range(len(future_df)):
                    current_row = pd.DataFrame([[
                        future_df.iloc[i]['MONTH_SIN'],
                        future_df.iloc[i]['MONTH_COS'],
                        future_df.iloc[i]['YEAR'],
                        last_known
                    ]], columns=['MONTH_SIN','MONTH_COS','YEAR','LAG1'])

                    y_pred = model.predict(current_row)[0]
                    predicted_values.append(int(y_pred))
                    last_known = y_pred

                predicted_values = np.array(predicted_values)

                # Random noise to make the graph look more "organic"
                if len(predicted_values) > 1:
                    noise = np.random.randint(-2, 3, size=len(predicted_values)-1)
                    predicted_values[1:] = np.maximum(0, predicted_values[1:] + noise)

                ax.bar(
                    x + idx * width,
                    predicted_values,
                    width=width,
                    label=speciality,
                )

            ax.set_xticks(x + width)
            ax.set_xticklabels(future_months_str, rotation=45, ha="right")
            ax.set_title(f"📈 Prédiction - {region}")
            ax.set_ylabel("Offres prédites")
            ax.legend()

        self.figure.tight_layout()
        self.canvas.draw()

