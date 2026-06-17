import pandas as pd
from manual_name_map import MANUAL_NAME_MAP

aamc = pd.read_csv("data/amcas_medical_schools_deadlines.csv")
shem = pd.read_csv("data/shemmassian_med_school_stats.csv")

# Map AAMC names to Shemmassian names
aamc["shemmassian_school_name"] = aamc["school_name"].map(MANUAL_NAME_MAP)

# Merge using the mapped Shemmassian name
merged = aamc.merge(
    shem,
    left_on="shemmassian_school_name",
    right_on="medical_school",
    how="left",
    suffixes=("_aamc", "_shemmassian")
)

merged.to_csv("data/merged_med_school_data.csv", index=False)

print(f"Merged rows: {len(merged)}")
print(merged.head())