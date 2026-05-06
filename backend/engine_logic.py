import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import calendar
from tensorflow.keras.models import load_model # type: ignore
from config import MODEL_PATHS, DATA_FILE_PATH
import os

models = {}
scalers = {}


BRAND_MAP = {
    'Metformin (500mg)': 0, 'Glilcomet': 0, 'Metfogen-XR': 0, 'Glucopet-XR': 0,
    'Gliclazide (80mg)': 1, 'Diamicron-MR': 1, 'Glycinorm': 1, 'Diatica': 1,
    'Sitagliptin (50mg)': 2, 'Sita': 2, 'Sitavic': 2, 'Nsit': 2,
    'Pioglitazone (30mg)': 3, 'Pioz': 3, 'Glustin': 3, 'Actos': 3,
    'Atorvastatin (20mg)': 4, 'Atova': 4, 'Lipitor': 4, 'Atovic': 4,
    'Losartan (50mg)': 5, 'Losacar': 5, 'Zaart': 5, 'Repace': 5,
    'Amlodipine (5mg)': 6, 'Amlong': 6, 'Amlopress': 6, 'Amlodac': 6,
    'Bisoprolol (5mg)': 7, 'Concor': 7, 'Bisovic': 7, 'Monocor': 7,
    'Thyroxine (100mcg)': 8, 'Euthyrox': 8, 'Thyronom': 8, 'TH (Levothyroxime)': 8,
    'Enalapril (5mg)': 9, 'Enam': 9, 'Envas': 9, 'Innovace': 9
}

def load_resources():
    try:
        scalers['X'] = joblib.load(MODEL_PATHS['scaler_X'])
        scalers['y'] = joblib.load(MODEL_PATHS['scaler_y'])
        models['lr'] = joblib.load(MODEL_PATHS['lr'])
        models['rf'] = joblib.load(MODEL_PATHS['rf'])
        models['xgb'] = joblib.load(MODEL_PATHS['xgb'])
        models['lstm'] = load_model(MODEL_PATHS['lstm'], compile=False)
        models['gru'] = load_model(MODEL_PATHS['gru'], compile=False)
        models['neurostack'] = joblib.load(MODEL_PATHS['neurostack'])
        print("System Ready: All Models & NeuroStack Loaded.")
    except Exception as e:
        print(f"CRITICAL ERROR Loading Resources: {e}")



def get_lag_12_demand(brand_name, target_month, target_year):
    try:
        if not os.path.exists(DATA_FILE_PATH): return 0.0
        df = pd.read_csv(DATA_FILE_PATH)
        df['Date'] = pd.to_datetime(df['Date'])
        lag_year = target_year - 1
        
        df['Brand_Clean'] = df['Brand_Name'].astype(str).str.strip().str.lower()
        search_brand = str(brand_name).strip().lower()
        
        record = df[(df['Brand_Clean'] == search_brand) & 
                    (df['Date'].dt.year == lag_year) & 
                    (df['Date'].dt.month == target_month)]
        
        if not record.empty:
            val = float(record.iloc[0]['Issued_Qty'])
            print(f"✅ FOUND: {brand_name} Lag-12 is {val}")
            return val
        

        avg = df[df['Brand_Clean'] == search_brand]['Issued_Qty'].mean()
        if pd.notna(avg):
            print(f"⚠️ INFO: Using brand average for {brand_name}: {avg}")
            return float(avg)
            
        print(f"DEBUG: No historical data found for {brand_name}")
        return 0.0
    except Exception as e:
        print(f"Error in get_lag_12_demand: {e}")
        return 0.0

def get_recent_actual(brand_name):
    try:
        if not os.path.exists(DATA_FILE_PATH): return 0.0
        df = pd.read_csv(DATA_FILE_PATH)
        
        df['Brand_Clean'] = df['Brand_Name'].astype(str).str.strip().str.lower()
        search_brand = str(brand_name).strip().lower()
        
        brand_df = df[df['Brand_Clean'] == search_brand].copy()
        
        if not brand_df.empty:
            brand_df['Date'] = pd.to_datetime(brand_df['Date'])
            val = brand_df.sort_values(by='Date').iloc[-1]['Issued_Qty']
            return float(val) if pd.notna(val) else 0.0
        return 0.0
    except Exception as e:
        print(f"Error in get_recent_actual: {e}")
        return 0.0


def prepare_input_features(brand_code, month, year, usd_rate, lag_12, recent_actual):
    expected_features = scalers['X'].feature_names_in_
    input_data = {feat: 0.0 for feat in expected_features}
    
    for feat in expected_features:
        if 'Brand' in feat: input_data[feat] = float(brand_code)
        elif 'Year' in feat: input_data[feat] = float(year)
        elif 'Month_Sin' in feat: input_data[feat] = np.sin(2 * np.pi * month / 12)
        elif 'Month_Cos' in feat: input_data[feat] = np.cos(2 * np.pi * month / 12)
        elif 'Month' in feat: input_data[feat] = float(month)
        elif 'USD' in feat: input_data[feat] = float(usd_rate)
        elif 'Lag_12' in feat: input_data[feat] = float(lag_12)
        elif any(x in feat for x in ['Lag', 'Rolling', 'Mean']):
            input_data[feat] = float(recent_actual)
            
    return pd.DataFrame([input_data])[expected_features]

def get_single_month_prediction(brand_code, month, year, usd_rate, lag_12, recent_actual):
    input_df = prepare_input_features(brand_code, month, year, usd_rate, lag_12, recent_actual)

    input_df = input_df.fillna(0.0)
    input_scaled = scalers['X'].transform(input_df)
    
    p_lr = models['lr'].predict(input_scaled).reshape(-1, 1)
    p_rf = models['rf'].predict(input_scaled).reshape(-1, 1)
    p_xgb = models['xgb'].predict(input_scaled).reshape(-1, 1)
    
    input_dl = input_scaled.reshape((1, 1, len(input_df.columns)))
    p_lstm = models['lstm'].predict(input_dl, verbose=0).reshape(-1, 1)
    p_gru = models['gru'].predict(input_dl, verbose=0).reshape(-1, 1)
    
    stack_input = pd.DataFrame({
        'LR': p_lr.ravel(), 'RF': p_rf.ravel(), 'XGB': p_xgb.ravel(), 
        'LSTM': p_lstm.ravel(), 'GRU': p_gru.ravel()
    })
    
    final_scaled = models['neurostack'].predict(stack_input).reshape(-1, 1)
    
    real_value = np.expm1(scalers['y'].inverse_transform(final_scaled)[0][0])
    return max(0, real_value)

def run_prediction(brand_name, current_stock, usd_rate):
    brand_code = BRAND_MAP.get(brand_name.strip(), -1)
    if brand_code == -1: 
        return {"error": f"Brand '{brand_name}' is not in the 30-product profile."}
    
    today = datetime.now()
    next_month = (today.month % 12) + 1
    next_year = today.year + (1 if today.month == 12 else 0)

    lag_12_next = get_lag_12_demand(brand_name, next_month, next_year)
    recent_actual = get_recent_actual(brand_name)

    final_prediction = get_single_month_prediction(
        brand_code, next_month, next_year, usd_rate, lag_12_next, recent_actual
    )

    _, days_in_next = calendar.monthrange(next_year, next_month)
    period_str = f"{next_year}-{next_month:02d}-01 to {next_year}-{next_month:02d}-{days_in_next}"

    return {
        "brand_name": brand_name,
        "prediction_period": period_str,
        "predicted_demand": round(final_prediction, 2),
        "applied_learning_weight": "NeuroStack Hybrid Optimized"
    }