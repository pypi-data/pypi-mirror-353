import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, PowerTransformer
from sklearn.compose import ColumnTransformer


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    """
    Construct a ColumnTransformer that scales numeric features and one-hot encodes categoricals.
    """
    # Identify feature types
    numeric_feats = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_feats = X.select_dtypes(include=["object", "category"]).columns.tolist()

    # Numeric pipeline
    num_pipe = Pipeline(
        [
            ("scaler", StandardScaler()),
        ]
    )

    # Categorical pipeline
    cat_pipe = Pipeline(
        [
            ("ohe", OneHotEncoder(sparse_output=False, handle_unknown="ignore")),
        ]
    )

    # Combine
    preprocessor = ColumnTransformer(
        [
            ("num", num_pipe, numeric_feats),
            ("cat", cat_pipe, categorical_feats),
        ]
    )

    return preprocessor


def build_target_transformer() -> PowerTransformer:
    """
    Returns a Yeo–Johnson power transformer for the target variable.
    """
    return PowerTransformer(method="yeo-johnson")
