import numpy as np
import pandas as pd
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error


def compute_metrics(y_true, y_pred):
    """
    Returns a dict of common regression metrics.
    """
    mse = mean_squared_error(y_true, y_pred)
    return {
        "R2": r2_score(y_true, y_pred),
        "MAE": mean_absolute_error(y_true, y_pred),
        "MSE": mse,
        "RMSE": np.sqrt(mse),
    }


def segment_metrics(df, group_col, y_true_col="true_CO2", y_pred_col="pred_CO2"):
    """
    Compute metrics per unique value in `group_col` of df.
    Returns a DataFrame with columns [group_col, Count, R2, MAE, RMSE].
    """
    records = []
    for seg, sub in df.groupby(group_col):
        yt = sub[y_true_col]
        yp = sub[y_pred_col]
        mets = compute_metrics(yt, yp)
        records.append({group_col: seg, "Count": len(sub), **mets})
    return pd.DataFrame(records).sort_values("R2", ascending=False)
