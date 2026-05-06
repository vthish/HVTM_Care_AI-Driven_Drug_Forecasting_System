import pandas as pd

file_path = 'drugs.csv'
df = pd.read_csv(file_path)

correct_dates_list = pd.date_range(start='2020-01-01', periods=73, freq='MS').strftime('%Y-%m-%d').tolist()
full_dates = correct_dates_list * 30

df['Date'] = full_dates
df.to_csv(file_path, index=False)

print("✅ File Updated Successfully.\n")

print("🔍 Verification (First Brand - 2020/2021 Pattern):")
print(df[['Date', 'Brand_Name']].iloc[0:15]) 

print("\n🔍 Verification (Middle Brand - Transition Check):")
print(df[['Date', 'Brand_Name']].iloc[70:80])