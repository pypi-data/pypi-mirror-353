import numpy as np
from sklearn.linear_model import Ridge
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score
import optuna
from lightgbm import LGBMRegressor
from xgboost import XGBRegressor
from catboost import CatBoostRegressor


def fit_cluster_model(X, y, preprocessor, target_transformer, n_trials=60):
    """
    Fit the stacked ensemble (3 GBMs + MLP meta-learner + Ridge residuals).
    Returns a dict bundling all fitted elements.
    """
    # Transform features and target
    Xp = preprocessor.fit_transform(X)
    yt = target_transformer.fit_transform(y.values.reshape(-1, 1)).ravel()

    def objective(trial):
        # Define base learners with trial-sampled hyperparams
        lgbm = LGBMRegressor(
            n_estimators=trial.suggest_int("lg_n", 300, 1500),
            learning_rate=trial.suggest_loguniform("lg_lr", 1e-3, 1e-1),
            num_leaves=trial.suggest_int("lg_leaves", 20, 150),
            reg_alpha=trial.suggest_loguniform("lg_a", 1e-3, 10),
            reg_lambda=trial.suggest_loguniform("lg_l", 1e-3, 10),
            random_state=42,
            verbosity=-1,
        )
        xgb = XGBRegressor(
            n_estimators=trial.suggest_int("xg_n", 300, 1500),
            learning_rate=trial.suggest_loguniform("xg_lr", 1e-3, 1e-1),
            max_depth=trial.suggest_int("xg_d", 3, 10),
            subsample=trial.suggest_uniform("xg_sub", 0.6, 1.0),
            colsample_bytree=trial.suggest_uniform("xg_col", 0.6, 1.0),
            random_state=42,
            verbosity=0,
        )
        cat = CatBoostRegressor(
            iterations=trial.suggest_int("ct_n", 300, 1500),
            learning_rate=trial.suggest_loguniform("ct_lr", 1e-3, 1e-1),
            depth=trial.suggest_int("ct_d", 3, 10),
            l2_leaf_reg=trial.suggest_loguniform("ct_l2", 1e-3, 10),
            random_state=42,
            verbose=0,
        )

        # 3-fold CV
        cv = KFold(3, shuffle=True, random_state=42)
        scores = []
        for tr_idx, va_idx in cv.split(Xp):
            Xtr, Xva = Xp[tr_idx], Xp[va_idx]
            ytr, yva = yt[tr_idx], yt[va_idx]
            # Fit base learners
            for m in (lgbm, xgb, cat):
                m.fit(Xtr, ytr)
            # Stack
            meta_X = np.vstack(
                [lgbm.predict(Xva), xgb.predict(Xva), cat.predict(Xva)]
            ).T
            # Meta-learner
            mlp = MLPRegressor(
                hidden_layer_sizes=(trial.suggest_int("mlp1", 50, 200),),
                alpha=trial.suggest_loguniform("mlp_l2", 1e-5, 1e-1),
                learning_rate_init=trial.suggest_loguniform("mlp_lr", 1e-4, 1e-2),
                max_iter=500,
                random_state=42,
            )
            mlp.fit(meta_X, yva)
            preds = mlp.predict(meta_X)
            scores.append(r2_score(yva, preds))
        return np.mean(scores)

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials)
    best = study.best_params

    # Refit base learners on full training data
    base1 = LGBMRegressor(
        n_estimators=best["lg_n"],
        learning_rate=best["lg_lr"],
        num_leaves=best["lg_leaves"],
        reg_alpha=best["lg_a"],
        reg_lambda=best["lg_l"],
        random_state=42,
        verbose=-1,
    )
    base2 = XGBRegressor(
        n_estimators=best["xg_n"],
        learning_rate=best["xg_lr"],
        max_depth=best["xg_d"],
        subsample=best["xg_sub"],
        colsample_bytree=best["xg_col"],
        random_state=42,
        verbosity=0,
    )
    base3 = CatBoostRegressor(
        iterations=best["ct_n"],
        learning_rate=best["ct_lr"],
        depth=best["ct_d"],
        l2_leaf_reg=best["ct_l2"],
        random_state=42,
        verbose=0,
    )

    for m in (base1, base2, base3):
        m.fit(Xp, yt)

    # Build meta features
    meta_X_full = np.vstack([base1.predict(Xp), base2.predict(Xp), base3.predict(Xp)]).T
    mlp_final = MLPRegressor(
        hidden_layer_sizes=(best["mlp1"],),
        alpha=best["mlp_l2"],
        learning_rate_init=best["mlp_lr"],
        max_iter=1000,
        random_state=42,
    )
    mlp_final.fit(meta_X_full, yt)

    # Residual correction
    resid = yt - mlp_final.predict(meta_X_full)
    ridge = Ridge(alpha=1.0)
    ridge.fit(meta_X_full, resid)

    return {
        "preprocessor": preprocessor,
        "target_transform": target_transformer,
        "base_models": (base1, base2, base3),
        "meta_model": mlp_final,
        "residual_model": ridge,
    }


def predict_bundle(bundle, X_new):
    """
    Given a fitted bundle, return inverse‐transformed predictions for new X.
    """
    pre = bundle["preprocessor"]
    tt = bundle["target_transform"]
    Xp = pre.transform(X_new)

    preds = np.vstack([m.predict(Xp) for m in bundle["base_models"]]).T
    meta_pred = bundle["meta_model"].predict(preds)
    corr = bundle["residual_model"].predict(preds)
    y_t = meta_pred + corr
    return tt.inverse_transform(y_t.reshape(-1, 1)).ravel()
