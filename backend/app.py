from fastapi import FastAPI, HTTPException # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from pydantic import BaseModel # type: ignore
from engine_logic import load_resources, run_prediction
from config import DATA_FILE_PATH
import pandas as pd
from datetime import datetime
import os
import math
import calendar

app = FastAPI(
    title="HVTM Care AI Backend",
    description="Medical Inventory Intelligence System",
    version="4.0.3" 
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CSV_COLUMNS = [
    'Date', 'Drug_Name', 'Brand_Name', 'Strength', 'Opening_Stock', 
    'Received_Qty', 'Issued_Qty', 'Closing_Stock', 'Shortage_Flag', 
    'Lead_Time', 'USD_Rate'
]

DRUG_STRENGTH_MAP = {
    "Metformin": ("Metformin", "500mg"), "Metfogen-XR": ("Metformin", "500mg"), "Glilcomet": ("Metformin", "500mg"), "Glucopet-XR": ("Metformin", "500mg"),
    "Gliclazide": ("Gliclazide", "80mg"), "Diamicron-MR": ("Gliclazide", "80mg"), "Diatica": ("Gliclazide", "80mg"), "Glycinorm": ("Gliclazide", "80mg"),
    "Sitagliptin": ("Sitagliptin", "50mg"), "Sita": ("Sitagliptin", "50mg"), "Sitavic": ("Sitagliptin", "50mg"), "Nsit": ("Sitagliptin", "50mg"),
    "Pioglitazone": ("Pioglitazone", "30mg"), "Pioz": ("Pioglitazone", "30mg"), "Glustin": ("Pioglitazone", "30mg"), "Actos": ("Pioglitazone", "30mg"),
    "Atorvastatin": ("Atorvastatin", "20mg"), "Atova": ("Atorvastatin", "20mg"), "Atovic": ("Atorvastatin", "20mg"), "Lipitor": ("Atorvastatin", "20mg"),
    "Losartan": ("Losartan", "50mg"), "Losacar": ("Losartan", "50mg"), "Zaart": ("Losartan", "50mg"), "Repace": ("Losartan", "50mg"),
    "Amlodipine": ("Amlodipine", "5mg"), "Amlodac": ("Amlodipine", "5mg"), "Amlong": ("Amlodipine", "5mg"), "Amlopress": ("Amlodipine", "5mg"),
    "Bisoprolol": ("Bisoprolol", "5mg"), "Bisovic": ("Bisoprolol", "5mg"), "Concor": ("Bisoprolol", "5mg"), "Monocor": ("Bisoprolol", "5mg"),
    "Thyroxine": ("Thyroxine", "100mcg"), "Euthyrox": ("Thyroxine", "100mcg"), "Thyronom": ("Thyroxine", "100mcg"), "TH (Levothyroxime)": ("Thyroxine", "100mcg"),
    "Enalapril": ("Enalapril", "5mg"), "Enam": ("Enalapril", "5mg"), "Envas": ("Enalapril", "5mg"), "Innovace": ("Enalapril", "5mg")
}

@app.on_event("startup")
def startup_event():
    load_resources()

class PredictionInput(BaseModel):
    brand_name: str
    current_stock: float
    usd_rate: float

class DataEntryInput(BaseModel):
    brand_name: str
    year: int
    month: int
    actual_issued_qty: float
    received_qty: float = 0.0 
    usd_rate: float

def check_duplicate_and_lock(brand, year, month):
    try:
        input_date = datetime(year, month, 1)
        current_date = datetime.now()
        if input_date > current_date:
            return False, f"Cannot enter data for future date: {year}-{month:02d}. Wait until the month begins."
    except ValueError:
        return False, "Invalid Date"

    if os.path.isfile(DATA_FILE_PATH):
        try:
            df = pd.read_csv(DATA_FILE_PATH)
            date_str = f"{year}-{month:02d}-01"
            existing = df[(df['Brand_Name'] == brand) & (df['Date'] == date_str)]
            if not existing.empty:
                return False, f"Data for {brand} in {year}-{month:02d} already exists. Please edit or delete it."
        except Exception as e:
            return False, str(e)
    return True, ""

def get_previous_stock_data(brand_name):
    opening_stock = 0.0
    lead_time = 14.0 
    if os.path.isfile(DATA_FILE_PATH):
        try:
            df = pd.read_csv(DATA_FILE_PATH)
            brand_df = df[df['Brand_Name'] == brand_name]
            if not brand_df.empty:
                brand_df['Date'] = pd.to_datetime(brand_df['Date'])
                brand_df = brand_df.sort_values(by='Date')
                last_record = brand_df.iloc[-1]
                opening_stock = float(last_record['Closing_Stock'])
                
                old_lead = float(last_record['Lead_Time'])
                lead_time = old_lead if old_lead > 0 else 14.0
        except:
            pass 
    return opening_stock, lead_time

@app.get("/data/logs")
def get_logs():
    if not os.path.exists(DATA_FILE_PATH):
        return []
    try:
        df = pd.read_csv(DATA_FILE_PATH)
        df = df.dropna(subset=['Date', 'Brand_Name'])
        return df.sort_values(by='Date', ascending=False).head(50).to_dict(orient='records')
    except:
        return []

@app.post("/predict")
def predict_endpoint(data: PredictionInput):
    raw_result = run_prediction(data.brand_name.strip(), data.current_stock, data.usd_rate)

    if isinstance(raw_result, dict) and "error" in raw_result:
        raise HTTPException(status_code=400, detail=raw_result["error"])

    raw_demand = float(raw_result.get('predicted_demand', 0))
    period_str = raw_result.get('prediction_period', "---")
    learning_status = raw_result.get('status', "NeuroStack Engine Active") 
 
    stable_demand = math.ceil(raw_demand)

    now = datetime.now()
    _, days_in_current_month = calendar.monthrange(now.year, now.month)
    remaining_days = days_in_current_month - now.day
    
    daily_demand_estimate = stable_demand / float(days_in_current_month)
    remaining_demand = daily_demand_estimate * remaining_days
    
    projected_closing_stock = data.current_stock - remaining_demand
    if projected_closing_stock < 0:
        projected_closing_stock = 0.0
        
    suggested_order = stable_demand - projected_closing_stock
    if suggested_order < 0:
        suggested_order = 0.0
        
    suggested_order = math.ceil(suggested_order)
    
    return {
        "brand_name": data.brand_name.strip(),
        "predicted_demand": stable_demand,
        "suggested_order_qty": suggested_order,
        "current_stock": data.current_stock,
        "prediction_period": period_str,
        "applied_learning_weight": learning_status,
        "projected_closing_stock": math.ceil(projected_closing_stock)
    }

@app.post("/data/add")
def add_data(data: DataEntryInput):
    try:
        clean_brand = data.brand_name.strip()
        is_valid, msg = check_duplicate_and_lock(clean_brand, data.year, data.month)
        if not is_valid:
            raise HTTPException(status_code=400, detail=msg)

        date_str = f"{data.year}-{data.month:02d}-01"
        drug_info = DRUG_STRENGTH_MAP.get(clean_brand, ("Unknown", "N/A"))
        
        opening_stock, lead_time = get_previous_stock_data(clean_brand)
        
        received = float(data.received_qty)
        issued = float(data.actual_issued_qty)
        
        closing_stock = (opening_stock + received) - issued
        if closing_stock < 0:
            closing_stock = 0.0

        shortage_flag = 0
        try:
            prediction_response = run_prediction(clean_brand, 0, data.usd_rate)
            predicted_demand = float(prediction_response.get('predicted_demand', 0)) if isinstance(prediction_response, dict) else float(prediction_response)
            stable_demand = math.ceil(predicted_demand)
            
            if stable_demand > issued:
                shortage_flag = 1
        except:
            shortage_flag = 0 

        new_row = {
            'Date': date_str,
            'Drug_Name': drug_info[0],
            'Brand_Name': clean_brand,
            'Strength': drug_info[1],
            'Opening_Stock': round(opening_stock, 2),
            'Received_Qty': round(received, 2),
            'Issued_Qty': round(issued, 2),
            'Closing_Stock': round(closing_stock, 2),
            'Shortage_Flag': shortage_flag,
            'Lead_Time': lead_time,
            'USD_Rate': data.usd_rate
        }
        
        df_new = pd.DataFrame([new_row])
        
        if not os.path.isfile(DATA_FILE_PATH):
            df_new.to_csv(DATA_FILE_PATH, index=False, columns=CSV_COLUMNS)
        else:
            df_new.to_csv(DATA_FILE_PATH, mode='a', header=False, index=False, columns=CSV_COLUMNS)
            
        return {"status": "success", "message": "Record synced successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/data/delete")
def delete_data(brand_name: str, date: str):
    try:
        if not os.path.isfile(DATA_FILE_PATH):
            raise HTTPException(status_code=404, detail="Dataset not found")
        df = pd.read_csv(DATA_FILE_PATH)
        df = df[~((df['Brand_Name'] == brand_name) & (df['Date'] == date))]
        df.to_csv(DATA_FILE_PATH, index=False)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))