import os

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    r2_score
)

import joblib


DATASET = (
    "datasets/processed/"
    "hot_cold_eviction_c16.csv"
)

MODEL_OUTPUT = (
    "models/memai_rf_c16.joblib"
)

RESULT_OUTPUT = (
    "results/memai_v1_offline.csv"
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
    "========== MemAI v1 =========="
)


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

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


# --------------------------------------------------
# Chronological split BY DECISION
#
# Never randomly split candidate rows because
# candidates from the same eviction decision
# must remain together.
# --------------------------------------------------

decision_ids = np.sort(
    df["decision_id"].unique()
)


split_index = int(
    len(decision_ids) * 0.70
)


train_decisions = decision_ids[
    :split_index
]

test_decisions = decision_ids[
    split_index:
]


train = df[
    df["decision_id"].isin(
        train_decisions
    )
].copy()


test = df[
    df["decision_id"].isin(
        test_decisions
    )
].copy()


print(
    "\nTrain decisions:",
    len(train_decisions)
)

print(
    "Test decisions:",
    len(test_decisions)
)

print(
    "Train rows:",
    len(train)
)

print(
    "Test rows:",
    len(test)
)


# --------------------------------------------------
# Features
# --------------------------------------------------

X_train = train[
    FEATURES
].copy()

X_test = test[
    FEATURES
].copy()


# --------------------------------------------------
# Target
#
# Reuse distance is extremely long-tailed.
#
# Transform:
#
#     y = log(1 + distance)
#
# --------------------------------------------------

y_train_raw = train[
    "next_use_distance"
].to_numpy()


y_test_raw = test[
    "next_use_distance"
].to_numpy()


y_train = np.log1p(
    y_train_raw
)


y_test = np.log1p(
    y_test_raw
)


# --------------------------------------------------
# Random Forest baseline
# --------------------------------------------------

model = RandomForestRegressor(
    n_estimators=50,

    max_depth=16,

    min_samples_leaf=8,

    max_features=0.8,

    # Reduce memory / training cost while keeping
    # a large chronological training set.
    max_samples=0.35,

    n_jobs=-1,

    random_state=42
)


print(
    "\nTraining model..."
)


model.fit(
    X_train,
    y_train
)


# --------------------------------------------------
# Prediction
# --------------------------------------------------

predicted_log_distance = (
    model.predict(
        X_test
    )
)


test["predicted_score"] = (
    predicted_log_distance
)


# --------------------------------------------------
# Standard regression metrics
# --------------------------------------------------

mae_log = mean_absolute_error(
    y_test,
    predicted_log_distance
)


r2_log = r2_score(
    y_test,
    predicted_log_distance
)


print(
    "\n========== REGRESSION =========="
)

print(
    "Log-distance MAE:",
    f"{mae_log:.4f}"
)

print(
    "Log-distance R2:",
    f"{r2_log:.4f}"
)


# --------------------------------------------------
# Decision-level evaluation
#
# This is much more important than regression MAE.
# --------------------------------------------------

# MemAI chooses candidate with maximum
# predicted future distance.

memai_indices = (
    test.groupby(
        "decision_id"
    )["predicted_score"]
    .idxmax()
)


memai_choice = test.loc[
    memai_indices,
    [
        "decision_id",
        "next_use_distance"
    ]
].copy()


memai_choice = memai_choice.rename(
    columns={
        "next_use_distance":
            "memai_distance"
    }
)


# --------------------------------------------------
# LRU choice
#
# lru_rank = 0 means oldest resident page.
# --------------------------------------------------

lru_choice = test[
    test["lru_rank"] == 0
][
    [
        "decision_id",
        "next_use_distance"
    ]
].copy()


lru_choice = lru_choice.rename(
    columns={
        "next_use_distance":
            "lru_distance"
    }
)


# --------------------------------------------------
# Oracle / OPT choice
# --------------------------------------------------

oracle = (
    test.groupby(
        "decision_id"
    )["next_use_distance"]
    .max()
    .reset_index()
)


oracle = oracle.rename(
    columns={
        "next_use_distance":
            "oracle_distance"
    }
)


# --------------------------------------------------
# Combine
# --------------------------------------------------

evaluation = oracle.merge(
    memai_choice,
    on="decision_id"
)


evaluation = evaluation.merge(
    lru_choice,
    on="decision_id"
)


# --------------------------------------------------
# Oracle-equivalent choice
#
# Ties are allowed:
# if multiple pages are never used again,
# any of them is an OPT-equivalent victim.
# --------------------------------------------------

evaluation[
    "memai_oracle_equivalent"
] = (
    evaluation["memai_distance"]
    ==
    evaluation["oracle_distance"]
)


evaluation[
    "lru_oracle_equivalent"
] = (
    evaluation["lru_distance"]
    ==
    evaluation["oracle_distance"]
)


memai_oracle_rate = (
    evaluation[
        "memai_oracle_equivalent"
    ].mean()
)


lru_oracle_rate = (
    evaluation[
        "lru_oracle_equivalent"
    ].mean()
)


# --------------------------------------------------
# Ranking regret
#
# 0 means the selected victim was OPT-equivalent.
#
# Use logarithms so extremely large reuse distances
# do not dominate the metric.
# --------------------------------------------------

evaluation[
    "memai_log_regret"
] = (
    np.log1p(
        evaluation[
            "oracle_distance"
        ]
    )
    -
    np.log1p(
        evaluation[
            "memai_distance"
        ]
    )
)


evaluation[
    "lru_log_regret"
] = (
    np.log1p(
        evaluation[
            "oracle_distance"
        ]
    )
    -
    np.log1p(
        evaluation[
            "lru_distance"
        ]
    )
)


memai_regret = (
    evaluation[
        "memai_log_regret"
    ].mean()
)


lru_regret = (
    evaluation[
        "lru_log_regret"
    ].mean()
)


print(
    "\n========== EVICTION QUALITY =========="
)


print(
    "LRU oracle-equivalent:",
    f"{lru_oracle_rate:.4f}"
)


print(
    "MemAI oracle-equivalent:",
    f"{memai_oracle_rate:.4f}"
)


print(
    "\nLRU mean log-regret:",
    f"{lru_regret:.4f}"
)


print(
    "MemAI mean log-regret:",
    f"{memai_regret:.4f}"
)


relative_improvement = (
    (
        lru_regret
        - memai_regret
    )
    / lru_regret
    * 100
    if lru_regret > 0
    else 0.0
)


print(
    "\nRegret reduction vs LRU:",
    f"{relative_improvement:.2f}%"
)


# --------------------------------------------------
# Feature importance
# --------------------------------------------------

importance = pd.DataFrame(
    {
        "feature": FEATURES,
        "importance":
            model.feature_importances_
    }
)


importance = importance.sort_values(
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


# --------------------------------------------------
# Save artifacts
# --------------------------------------------------

os.makedirs(
    "models",
    exist_ok=True
)


os.makedirs(
    "results",
    exist_ok=True
)


joblib.dump(
    {
        "model": model,
        "features": FEATURES
    },
    MODEL_OUTPUT,
    compress=3
)


summary = pd.DataFrame(
    [
        {
            "model":
                "RandomForestRegressor",

            "capacity":
                16,

            "train_decisions":
                len(train_decisions),

            "test_decisions":
                len(test_decisions),

            "log_mae":
                mae_log,

            "log_r2":
                r2_log,

            "lru_oracle_equivalent":
                lru_oracle_rate,

            "memai_oracle_equivalent":
                memai_oracle_rate,

            "lru_log_regret":
                lru_regret,

            "memai_log_regret":
                memai_regret,

            "regret_reduction_percent":
                relative_improvement
        }
    ]
)


summary.to_csv(
    RESULT_OUTPUT,
    index=False
)


print(
    "\nModel:",
    MODEL_OUTPUT
)


print(
    "Results:",
    RESULT_OUTPUT
)
