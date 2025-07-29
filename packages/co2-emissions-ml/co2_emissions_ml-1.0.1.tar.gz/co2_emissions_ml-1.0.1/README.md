# CO₂ Emissions Prediction from Vehicle Features

**Authors:** Shashvat Jain  
**Affiliation:** Integrated M.Tech. in Mathematics & Computing, IIT Dhanbad  
**GitHub:** https://github.com/Shashvat-Jain/CO2-predictions-using-Automotive-Features

---

# co2_emissions_ml

**CO₂ Emissions Prediction from Vehicle Features**  
End-to-end Python package for analyzing and predicting on-road vehicle CO₂ emissions (g/km) via machine learning.

## Features

- **Preprocessing & Feature Engineering**: scaling, one-hot encoding, target transformation
- **Baseline Models**: linear, polynomial, ridge/lasso, random forest, XGBoost, LightGBM, CatBoost
- **Stacked Ensemble**: LightGBM + XGBoost + CatBoost → MLP meta-learner → Ridge residual correction
- **Bayesian Hyperparameter Tuning**: Optuna pruners, early stopping
- **Diagnostics & Explainability**: parity plots, residual analysis, learning curves, permutation importance, SHAP

Key result:

> **Test set**: (R^2 = 0.9830), MAE ≈ 3.08 g/km, RMSE ≈ 8.64 g/km

---

## 📦 Repository Structure

```bash
.
├── README.md
├── LICENSE
├── CITATION.cff
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── DATA_DICTIONARY.md
├── .gitignore
├── environment.yml
├── requirements.txt
├── setup.py
├── Dockerfile
│
├── data/
│ └── New Dataset.csv
│
├── notebooks/
│ └── co2-emissions-predict.ipynb
│
├── src/
│ ├──models
│ └──co2_emissions_ml
│    ├── __init__.py
│    ├── preprocessing.py
│    ├── models.py
│    ├── evaluation.py
│    └── pipeline.py
│
├── tests/
│ └── test_pipeline.py
│
├── scripts/
│ └── train_and_save.py
│
├── Figures/
│ ├── parity_plot.png
│ ├── residual_hist.png
│ ├── qq_plot.png
│ ├── residuals_vs_pred.png
│ ├── mae_decile.png
│ ├── learning_curve.png
│ ├── perm_importance.png
│ ├── shap_summary.png
│ ├── shap_dependence.png
│ └── pipeline_diagram.png
│
├── Slides/
│ └── End Evaluation.pdf
│
└── Reports/
├── Split Report
└── Final Report with plag report.pdf
```

---

## ⚙️ Installation

```bash
# From PyPI
pip install co2_emissions_ml

# Or install latest from GitHub
pip install git+https://github.com/Shashvat-Jain/CO2-predictions-using-Automotive-Features.git
```

## Quickstart

1. **Predict via CLI**

```bash
run_co2 \
  --data path/to/your_new_data.csv \
  --model path/to/pretrained_bundle.pkl \
  --output path/to/predictions.csv
```

- --data (required): input CSV with vehicle features

- --model (optional): path to serialized bundle.pkl (default: models/bundle.pkl)

- --output (optional): CSV path for predictions

- --target (optional): dependent variable name in input CSV

2. **Programmatic API**

```python
import pandas as pd
import joblib
from co2_emissions_ml.models import predict_bundle

# Load pre-trained bundle
bundle = joblib.load("models/bundle.pkl")

# Prepare new data
df_new = pd.read_csv("your_new_data.csv")
X_new  = df_new.copy()

# Predict
df_new["predicted_CO2"] = predict_bundle(bundle, X_new)
df_new.to_csv("predictions.csv", index=False)
```

## 🚀 Usage of GitHub Repository

1. **Prepare data**
   Place New Dataset.csv under data/.

2. **Run notebook**
   Open and execute notebooks/co2_emissions_predict.ipynb to reproduce EDA, model training, and evaluation.

3. **Diagnostics & plots**
   Generated in figures/:
   - Parity plot
   - Residual histogram & Q-Q plot
   - Learning curve
   - Permutation & SHAP importance charts

Note: The notebook co2_emissions_predict.ipynb contains the complete code for the thesis whereas the src folder only contains the code for the new pipeline presented in this research.

## 📊 Results Snapshot

Figure: ![Predicted vs. True CO₂ Emissions](Figures/Parity%20Plot.png)
Figure: ![Learning Curve](<Figures/Learning%20Curve%20(R2).png>)

## 📚 References

- Smith A., Jones B., Lee C. (2020). Random Forest–Based Prediction of Vehicle CO₂ Emissions. Int. J. Automotive Technol.

- Gupta R., Ramesh S. (2021). XGBoost Regression for Estimating Vehicle Emissions. IEEE Trans. Intelligent Vehicles.

- Tansini A., Pavlović I., Fontaras G. (2022). Forecasting CO₂ Emissions Using Ensemble, ML & DL. PeerJ.

- Zhao P., Zhang X., Li Y. (2023). Global Fuel- and Vehicle-Type-Specific CO₂ Emissions. Earth Syst. Sci. Data.

- Government of Canada (2024). Fuel Consumption Ratings. Open Gov. Portal.

- U.S. EPA (2022). 2022 EPA Automotive Trends Report. EPA-420-S-22-001.

- (See full bibliography in reports/.)

## 📄 License

This project is licensed under the MIT License. See LICENSE for details.
