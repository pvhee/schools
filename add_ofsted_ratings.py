import pandas as pd

# Read existing geocoded schools data
schools_df = pd.read_csv('schools_ofsted_london.csv')

# Read Ofsted inspection data
ofsted_df = pd.read_csv('data/State_funded_schools_inspections_and_outcomes_as_at_31_December_2024.csv', 
                        low_memory=False, encoding='latin1')

print(f"Ofsted data loaded: {len(ofsted_df)} schools")
common_urns = set(schools_df['URN']).intersection(set(ofsted_df['URN']))
print(f"Schools with Ofsted data: {len(common_urns)} out of {len(schools_df)}")

# Ensure URN columns are the same type (int)
schools_df['URN'] = schools_df['URN'].astype(int)
ofsted_df['URN'] = ofsted_df['URN'].astype(int)

# Select relevant columns from Ofsted data
ofsted_subset = ofsted_df[['URN', 'Overall effectiveness', 'Inspection start date']].copy()

# Remove duplicates (keep first inspection for each school)
ofsted_subset = ofsted_subset.drop_duplicates(subset='URN', keep='first')

# Merge on URN
merged = pd.merge(schools_df, ofsted_subset, on='URN', how='left')

# Map ratings to text labels (handle both numeric and string values)
rating_map = {
    '1': "Outstanding",
    '2': "Good", 
    '3': "Requires Improvement",
    '4': "Inadequate",
    1: "Outstanding",
    2: "Good", 
    3: "Requires Improvement",
    4: "Inadequate",
    'Not judged': "Not judged"
}

# Convert to string first to handle mixed types
merged["Overall effectiveness"] = merged["Overall effectiveness"].astype(str)
merged["Ofsted Rating"] = merged["Overall effectiveness"].map(rating_map)

# Save updated CSV
merged.to_csv('schools_ofsted_london_with_ratings.csv', index=False)

# Show statistics
print(f"Total schools: {len(merged)}")
print(f"\nOfsted ratings breakdown:")
print(merged["Ofsted Rating"].value_counts())
print(f"\nSchools without rating: {merged['Ofsted Rating'].isna().sum()}")