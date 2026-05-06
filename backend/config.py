import os

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

DATA_FILE_PATH = os.path.join(PROJECT_ROOT, "drugs.csv")
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")

MODEL_PATHS = {
    "scaler_X": os.path.join(MODEL_DIR, "scaler_X.pkl"),
    "scaler_y": os.path.join(MODEL_DIR, "scaler_y.pkl"),
    "lr": os.path.join(MODEL_DIR, "linear_regression_model.pkl"), 
    "rf": os.path.join(MODEL_DIR, "random_forest_model.pkl"),
    "xgb": os.path.join(MODEL_DIR, "xgboost_model.pkl"),
    "lstm": os.path.join(MODEL_DIR, "BiLSTM_model.h5"),
    "gru": os.path.join(MODEL_DIR, "GRU_model.h5"),
    

    "neurostack": os.path.join(MODEL_DIR, "NeuroStack_MetaLearner.pkl")
}