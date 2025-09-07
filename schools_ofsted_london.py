import os
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Constants
POSTCODE = "N16 7RJ"
RADIUS_MILES = 10

import os
# Use local GIAS school data
SCHOOLS_PATH = "data/edubasealldata.csv"
# Ofsted inspection data (user must provide or download manually)
OFSTED_PATH = "data/State_funded_schools_inspections_and_outcomes_as_at_31_December_2024.csv"  # Update this path as needed

# Helper: get lat/lon for postcode
geolocator = Nominatim(user_agent="school_locator")
location = geolocator.geocode(POSTCODE)
if not location:
    raise Exception(f"Could not geocode postcode {POSTCODE}")
center = (location.latitude, location.longitude)

if not os.path.exists(SCHOOLS_PATH):
    raise FileNotFoundError(f"School data not found at {SCHOOLS_PATH}")
gias_df = pd.read_csv(SCHOOLS_PATH, low_memory=False, encoding='latin1')

secondary = gias_df[(gias_df["PhaseOfEducation (name)"] == "Secondary") & (gias_df["Town"] == "London")]
secondary = secondary.dropna(subset=["Postcode"])

def geocode_postcode(postcode):
    try:
        loc = geolocator.geocode(postcode)
        if loc:
            return (loc.latitude, loc.longitude)
    except Exception:
        pass
    return (None, None)

secondary["latlon"] = secondary["Postcode"].apply(geocode_postcode)
secondary = secondary.dropna(subset=["latlon"])
secondary["Latitude"] = secondary["latlon"].apply(lambda x: x[0])
secondary["Longitude"] = secondary["latlon"].apply(lambda x: x[1])
# Remove rows with NaN coordinates
secondary = secondary.dropna(subset=["Latitude", "Longitude"])
def within_radius(row):
    school_loc = (row["Latitude"], row["Longitude"])
    return geodesic(center, school_loc).miles <= RADIUS_MILES
secondary = secondary[secondary.apply(within_radius, axis=1)]

if not os.path.exists(OFSTED_PATH):
    print(f"Ofsted data not found at {OFSTED_PATH}. Please download and place the file.")
    ofsted_df = pd.DataFrame()
else:
    ofsted_df = pd.read_csv(OFSTED_PATH, low_memory=False, encoding='latin1')

# Merge on URN if Ofsted data is available
if not ofsted_df.empty:
    merged = pd.merge(secondary, ofsted_df, left_on="URN", right_on="URN", how="left")
    # Output for mapping - include key columns
    out_cols = ["EstablishmentName", "URN", "Latitude", "Longitude"]
    
    # Include Ofsted rating column
    if "Overall effectiveness" in merged.columns:
        out_cols.append("Overall effectiveness")
        # Map numeric ratings to text labels
        rating_map = {
            1: "Outstanding",
            2: "Good", 
            3: "Requires Improvement",
            4: "Inadequate"
        }
        merged["Ofsted Rating"] = merged["Overall effectiveness"].map(rating_map)
        out_cols.append("Ofsted Rating")
    
    # Include latest inspection date if available
    if "Inspection start date" in merged.columns:
        out_cols.append("Inspection start date")
    
    merged_out = merged[out_cols]
else:
    merged_out = secondary[["EstablishmentName", "URN", "Latitude", "Longitude"]]

merged_out.to_csv("schools_ofsted_london.csv", index=False)
print(f"Saved schools_ofsted_london.csv with {len(merged_out)} schools")
print(f"Columns included: {', '.join(merged_out.columns)}")
