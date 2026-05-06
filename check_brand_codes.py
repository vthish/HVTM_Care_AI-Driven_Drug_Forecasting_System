import pandas as pd
from sklearn.preprocessing import LabelEncoder

file_path = 'drugs.csv' 
df = pd.read_csv(file_path)

le = LabelEncoder()
le.fit(df['Brand_Name'])

print("\n📋 BRAND CODE REFERENCE LIST")
print("=" * 40)
print(f"{'CODE':<5} | {'BRAND NAME'}")
print("-" * 40)

brand_mapping = dict(zip(le.transform(le.classes_), le.classes_))

for code, name in brand_mapping.items():
    print(f"{code:<5} | {name}")

print("=" * 40)