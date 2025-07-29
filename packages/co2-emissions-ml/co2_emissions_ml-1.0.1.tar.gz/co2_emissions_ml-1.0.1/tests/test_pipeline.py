import pandas as pd
import numpy as np
import tempfile
from co2_emissions_ml.pipeline import run_pipeline
from co2_emissions_ml.preprocessing import build_preprocessor, build_target_transformer


def make_toy_data(n=50):
    # minimal synthetic data with same columns
    rng = np.random.RandomState(0)
    df = pd.DataFrame(
        {
            "Engine Size (L)": rng.uniform(1.0, 3.0, n),
            "Cylinders": rng.choice([4, 6, 8], n),
            "Fuel Consumption City (L/100 km)": rng.uniform(5, 15, n),
            "Fuel Consumption Hwy (L/100 km)": rng.uniform(4, 10, n),
            "Fuel Consumption Comb (L/100 km)": rng.uniform(4, 12, n),
            "Fuel Type": rng.choice(["Gasoline", "Diesel"], n),
            "Transmission": rng.choice(["Automatic", "Manual"], n),
            "Vehicle Class": rng.choice(["SUV", "Sedan", "Truck"], n),
            "CO2 Emissions (g/km)": rng.uniform(100, 300, n),
        }
    )
    return df


def test_run_pipeline_smoke(tmp_path):
    df = make_toy_data()
    path = tmp_path / "toy.csv"
    df.to_csv(path, index=False)
    bundle, metrics = run_pipeline(str(path))
    # basic sanity checks
    assert 0.0 <= metrics["R2"] <= 1.0
    assert metrics["RMSE"] >= 0
