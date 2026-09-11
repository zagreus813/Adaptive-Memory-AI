import os

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor


DATASET = (
    "datasets/processed/"
    "hot_cold_train_eviction_c16.csv"
)

MODEL_OUTPUT = (
    "models/"
    "memai_rf_hotcold_train_c16.joblib"
)


FEATURES = [
    "access_count",
    "read_count",
    "write_count",
    "time_since_last_access",
    "access_frequency",
    "mean_reuse_gap",
    "read_ratio",
    "write_ratio",
    "resident_age",
    "lru_rank"
]


print(
    "========== MemAI Unseen-Trace Training =========="
)


df = pd.read_csv(
    DATASET
)


print(
    "Rows:",
    len(df)
)

print(
    "Decisions:",
    df["decision_id"].nunique()
)


X = df[
    FEATURES
]


# Predict log(next-use-distance).
y = np.log1p(
    df[
        "next_use_distance"
    ].to_numpy()
)


model = RandomForestRegressor(
    n_estimators=50,
    max_depth=16,
    min_samples_leaf=8,
    max_features=0.8,
    max_samples=0.35,
    n_jobs=-1,
    random_state=42
)


print(
    "\nTraining..."
)


model.fit(
    X,
    y
)


print(
    "Training finished."
)


# --------------------------------
# Feature importance
# --------------------------------

importance = pd.DataFrame(
    {
        "feature": FEATURES,
        "importance":
            model.feature_importances_
    }
).sort_values(
    "importance",
    ascending=False
)


print(
    "\n========== FEATURE IMPORTANCE =========="
)

print(
    importance.to_string(
        index=False
    )
)


# --------------------------------
# Save
# --------------------------------

os.makedirs(
    "models",
    exist_ok=True
)


joblib.dump(
    {
        "model": model,
        "features": FEATURES,
        "capacity": 16,
        "training_seed": 1111
    },
    MODEL_OUTPUT,
    compress=3
)


print(
    "\nModel:",
    MODEL_OUTPUT
)
