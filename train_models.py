import os
import pickle
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

# -----------------------------
# Create models directory
# -----------------------------
os.makedirs("models", exist_ok=True)

# -----------------------------
# Synthetic but realistic variant feature set
# -----------------------------
np.random.seed(42)

N = 5000

data = pd.DataFrame({
    "REF_len": np.random.randint(1, 5, N),
    "ALT_len": np.random.randint(1, 5, N),
    "QUAL": np.random.uniform(10, 200, N),
    "AF_EUR": np.random.beta(0.5, 5, N),
    "AF_AFR": np.random.beta(0.8, 4, N),
    "AF_EAS": np.random.beta(0.6, 4, N),
})

# Pathogenic label logic (non-random)
data["pathogenic"] = (
    (data["QUAL"] > 80) &
    (data["AF_EUR"] < 0.01) &
    (data["ALT_len"] > 1)
).astype(int)

X = data.drop(columns=["pathogenic"])
y = data["pathogenic"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42
)

# -----------------------------
# Train models
# -----------------------------
rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    random_state=42,
    n_jobs=-1
)

lr = LogisticRegression(max_iter=2000)

xgb = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.9,
    colsample_bytree=0.9,
    eval_metric="logloss",
    random_state=42
)

rf.fit(X_train, y_train)
lr.fit(X_train, y_train)
xgb.fit(X_train, y_train)

# -----------------------------
# Save models
# -----------------------------
with open("models/rf_model.pkl", "wb") as f:
    pickle.dump(rf, f)

with open("models/lr_model.pkl", "wb") as f:
    pickle.dump(lr, f)

with open("models/xgb_model.pkl", "wb") as f:
    pickle.dump(xgb, f)

print("Models trained and saved successfully.")
