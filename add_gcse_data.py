import pandas as pd

# Read existing school data with Ofsted ratings
schools_df = pd.read_csv('schools_ofsted_london_with_ratings.csv')

# Read GCSE/KS4 performance data
gcse_df = pd.read_csv('data/ks4_school_info_2024.csv')

print(f"Schools data: {len(schools_df)} schools")
print(f"GCSE data: {len(gcse_df)} schools")

# Key columns in GCSE data:
# - school_urn: URN to match with our data
# - diffn_p8mea: Progress 8 score (how much progress students make compared to similar students nationally)
# - p8_banding: Progress 8 banding (Well above average, Above average, Average, Below average, Well below average)
# - diffn_att8: Attainment 8 score difference from national average

# Merge on URN
merged = pd.merge(schools_df, gcse_df[['school_urn', 'diffn_p8mea', 'p8_banding', 'diffn_att8']], 
                  left_on='URN', right_on='school_urn', how='left')

# Clean up the data
merged = merged.drop('school_urn', axis=1)

# Replace 'z' values with NaN (z means data suppressed for privacy)
merged['diffn_p8mea'] = merged['diffn_p8mea'].replace('z', None)
merged['diffn_att8'] = merged['diffn_att8'].replace('z', None)
merged['p8_banding'] = merged['p8_banding'].replace('z', None)

# Convert numeric columns
merged['diffn_p8mea'] = pd.to_numeric(merged['diffn_p8mea'], errors='coerce')
merged['diffn_att8'] = pd.to_numeric(merged['diffn_att8'], errors='coerce')

# Save the updated data
merged.to_csv('schools_london_complete.csv', index=False)

# Show statistics
print(f"\nMerged data: {len(merged)} schools")
print(f"Schools with Progress 8 data: {merged['diffn_p8mea'].notna().sum()}")
print(f"Schools with Attainment 8 data: {merged['diffn_att8'].notna().sum()}")

print("\nProgress 8 Banding distribution:")
print(merged['p8_banding'].value_counts())

print("\nTop 10 schools by Progress 8 score:")
top_p8 = merged[merged['diffn_p8mea'].notna()].nlargest(10, 'diffn_p8mea')
for _, school in top_p8.iterrows():
    print(f"  {school['EstablishmentName']}: +{school['diffn_p8mea']:.2f} ({school['p8_banding']}) - Ofsted: {school['Ofsted Rating']}")

print("\nProgress 8 Score Guide:")
print("  +1.0 or above = Well above average")
print("  +0.5 to +1.0 = Above average") 
print("  -0.5 to +0.5 = Average")
print("  -1.0 to -0.5 = Below average")
print("  -1.0 or below = Well below average")