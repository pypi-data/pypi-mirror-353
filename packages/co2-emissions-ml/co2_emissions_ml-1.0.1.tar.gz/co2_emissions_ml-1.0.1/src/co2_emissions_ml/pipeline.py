import pandas as pd
from co2_emissions_ml.preprocessing import build_preprocessor, build_target_transformer
from co2_emissions_ml.models import fit_cluster_model, predict_bundle
from co2_emissions_ml.evaluation import compute_metrics
from sklearn.model_selection import train_test_split
import argparse, joblib, os


def run_pipeline(
    data_path: str,
    target_col: str = None,
):
    # 1) Load data
    try:
        df = pd.read_csv(data_path)
    except UnicodeDecodeError:
        # fall back to latin-1 for files with extended characters
        print(f"[WARN] UTF-8 decode failed, retrying with latin-1 for {data_path}")
        df = pd.read_csv(data_path, encoding="latin-1")
    # If no target_col given, try to auto-detect
    if target_col is None:
        # pick the one column containing "CO2" or "Emissions"
        candidates = [
            c for c in df.columns if "co2" in c.lower() or "emiss" in c.lower()
        ]
        if not candidates:
            raise KeyError(
                "No target column specified and no column matching 'CO2' or 'Emissions' found."
            )
        # use the longest match (to avoid 'Transmission' matching 'transmission')
        target_col = max(candidates, key=len)
        print(f"[INFO] Auto-detected target column: '{target_col}'")

    if target_col not in df.columns:
        raise KeyError(
            f"Target column '{target_col}' not found in data. Available columns: {df.columns.tolist()}"
        )

    X = df.drop(columns=[target_col])
    y = df[target_col]

    # 2) Build preprocessing objects
    pre = build_preprocessor(X)
    tt = build_target_transformer()

    # 3) Fit ensemble
    bundle = fit_cluster_model(X, y, pre, tt)

    # 4) Evaluate on train & test split

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
    y_pred = predict_bundle(bundle, X_te)

    # 5) Metrics
    metrics = compute_metrics(y_te, y_pred)
    print("Test set performance:")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}")

    return bundle, metrics


DEFAULT_MODEL = os.path.join(os.path.dirname(__file__), "..", "models", "bundle.pkl")


def main():
    parser = argparse.ArgumentParser(
        description="Train & evaluate the CO₂ emissions pipeline"
    )
    parser.add_argument(
        "--model",
        dest="model_path",
        type=str,
        default=DEFAULT_MODEL,
        help="Path to pre-trained bundle (for inference).",
    )

    parser.add_argument("--data", dest="data_path", type=str, required=True)
    parser.add_argument("--target", dest="target_col", type=str, default=None)
    parser.add_argument("--output", dest="out_csv", type=str, default=None)
    args = parser.parse_args()

    # If model_path exists, run in inference‐only mode
    if os.path.exists(args.model_path) and args.target_col is None:
        print(f"[INFO] Loading pre-trained bundle from {args.model_path}")
        bundle = joblib.load(args.model_path)

        # Pure inference: read data, predict, write out
        try:
            df = pd.read_csv(args.data_path)
        except UnicodeDecodeError:
            print(
                f"[WARN] UTF-8 decode failed, retrying with latin-1 for {args.data_path}"
            )
            df = pd.read_csv(args.data_path, encoding="latin-1")

        X_new = df.copy()
        preds = predict_bundle(bundle, X_new)
        df["predicted_CO2"] = preds
        if args.out_csv:
            df.to_csv(args.out_csv, index=False)
            print(f"[INFO] Wrote predictions to {args.out_csv}")
        else:
            print(df.head())
        return

    # Otherwise, fall back to full training+evaluation
    bundle, metrics = run_pipeline(args.data_path, args.target_col)

    # If user wants raw predictions on every row:
    if args.out_csv:
        try:
            df = pd.read_csv(args.data_path)
        except UnicodeDecodeError:
            print(
                f"[WARN] UTF-8 decode failed, retrying with latin-1 for {args.data_path}"
            )
            df = pd.read_csv(args.data_path, encoding="latin-1")
        # drop target if present
        if args.target_col in df.columns:
            X = df.drop(columns=[args.target_col])
        else:
            X = df
        df["predicted_CO2"] = predict_bundle(bundle, X)
        df.to_csv(args.out_csv, index=False)
        print(f"[INFO] Wrote predictions to {args.out_csv}")


if __name__ == "__main__":
    main()
