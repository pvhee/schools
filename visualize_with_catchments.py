import pandas as pd
import folium
from folium import plugins
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import json

# Read the CSV data with Ofsted ratings
df = pd.read_csv('schools_ofsted_london_with_ratings.csv')

# Get accurate coordinates for N16 7RJ
geolocator = Nominatim(user_agent="school_locator")
home_location = geolocator.geocode("N16 7RJ, London, UK")
home_lat = home_location.latitude if home_location else 51.5645
home_lon = home_location.longitude if home_location else -0.0759

print(f"Home location (N16 7RJ): {home_lat}, {home_lon}")

# Create a map centered around the home location
m = folium.Map(location=[home_lat, home_lon], zoom_start=12)

# Add home location marker
folium.Marker(
    [home_lat, home_lon],
    popup='Home (N16 7RJ)',
    tooltip='Home Location',
    icon=folium.Icon(color='red', icon='home', prefix='fa')
).add_to(m)

# Add a circle to show the 10-mile radius
folium.Circle(
    radius=16093.4,  # 10 miles in meters
    location=[home_lat, home_lon],
    popup='10 mile radius',
    color='crimson',
    fill=False,
    weight=2,
    opacity=0.5
).add_to(m)

# Define colors for Ofsted ratings
rating_colors = {
    'Outstanding': 'green',
    'Good': 'blue',
    'Requires Improvement': 'orange',
    'Inadequate': 'red',
    'Not judged': 'gray',
    'nan': 'lightgray'
}

# Typical catchment distances based on school rating and type
# These are approximations based on London school data
catchment_distances = {
    'Outstanding': 800,  # meters - highly sought after schools have tighter catchments
    'Good': 1200,  # meters
    'Requires Improvement': 2000,  # meters - typically have larger catchments
    'Inadequate': 2500,  # meters
    'Not judged': 1500,  # meters - average
    'nan': 1500  # default for schools without ratings
}

# Create feature groups for different elements
school_markers = folium.FeatureGroup(name='Schools', show=True)
catchment_areas = folium.FeatureGroup(name='Catchment Areas (Estimated)', show=False)

# Add school markers with catchment areas
for idx, row in df.iterrows():
    # Calculate distance from home
    school_loc = (row['Latitude'], row['Longitude'])
    home_loc = (home_lat, home_lon)
    distance_meters = geodesic(home_loc, school_loc).meters
    distance_miles = geodesic(home_loc, school_loc).miles
    
    # Get the rating and color
    rating = str(row['Ofsted Rating']) if pd.notna(row['Ofsted Rating']) else 'No rating'
    color = rating_colors.get(row['Ofsted Rating'], 'lightgray')
    
    # Get estimated catchment distance
    catchment_radius = catchment_distances.get(row['Ofsted Rating'], 1500)
    
    # Create popup text with school info
    popup_text = f"""
    <b>{row['EstablishmentName']}</b><br>
    <b>📍 Distance from home: {distance_meters:.0f}m ({distance_miles:.1f} miles)</b><br>
    URN: {row['URN']}<br>
    <b>Ofsted Rating: {rating}</b><br>
    <i>Estimated catchment: ~{catchment_radius}m</i>
    """
    
    # Add inspection date if available
    if pd.notna(row['Inspection start date']):
        popup_text += f"<br>Last Inspection: {row['Inspection start date']}"
    
    # Add marker for each school
    folium.Marker(
        [row['Latitude'], row['Longitude']],
        popup=folium.Popup(popup_text, max_width=300),
        tooltip=f"{row['EstablishmentName']} - {rating} - {distance_meters:.0f}m from home",
        icon=folium.Icon(color=color, icon='graduation-cap', prefix='fa')
    ).add_to(school_markers)
    
    # Add catchment area circle (semi-transparent)
    folium.Circle(
        location=[row['Latitude'], row['Longitude']],
        radius=catchment_radius,
        popup=f"{row['EstablishmentName']} - Estimated catchment area",
        color=color,
        fill=True,
        fillOpacity=0.1,
        opacity=0.3,
        weight=1
    ).add_to(catchment_areas)

# Add feature groups to map
school_markers.add_to(m)
catchment_areas.add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

# Add a legend
legend_html = '''
<div style="position: fixed; 
            bottom: 50px; right: 50px; width: 250px; height: auto; 
            background-color: white; z-index:9999; font-size:14px;
            border:2px solid grey; border-radius:5px; padding: 10px">
<h4 style="margin: 0;">Ofsted Ratings</h4>
<p style="margin: 5px;"><i class="fa fa-graduation-cap" style="color:green;"></i> Outstanding (~800m catchment)</p>
<p style="margin: 5px;"><i class="fa fa-graduation-cap" style="color:blue;"></i> Good (~1200m catchment)</p>
<p style="margin: 5px;"><i class="fa fa-graduation-cap" style="color:orange;"></i> Requires Improvement (~2000m)</p>
<p style="margin: 5px;"><i class="fa fa-graduation-cap" style="color:red;"></i> Inadequate (~2500m)</p>
<p style="margin: 5px;"><i class="fa fa-graduation-cap" style="color:gray;"></i> Not Judged (~1500m)</p>
<p style="margin: 5px;"><i class="fa fa-graduation-cap" style="color:lightgray;"></i> No Rating (~1500m)</p>
<p style="margin: 5px;"><i class="fa fa-home" style="color:red;"></i> Home Location (N16 7RJ)</p>
<br>
<p style="margin: 5px; font-size:12px;"><i>Note: Catchment areas are estimates based on typical distances. Actual catchments vary by year and demand.</i></p>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Add fullscreen button
plugins.Fullscreen().add_to(m)

# Find schools within typical catchment distance from home
schools_in_catchment = []
for idx, row in df.iterrows():
    school_loc = (row['Latitude'], row['Longitude'])
    home_loc = (home_lat, home_lon)
    distance = geodesic(home_loc, school_loc).meters
    
    # Get the catchment radius for this school
    catchment_radius = catchment_distances.get(row['Ofsted Rating'], 1500)
    
    if distance <= catchment_radius:
        schools_in_catchment.append({
            'name': row['EstablishmentName'],
            'rating': row['Ofsted Rating'],
            'distance': round(distance),
            'catchment': catchment_radius
        })

# Sort by distance
schools_in_catchment.sort(key=lambda x: x['distance'])

# Save the map
m.save('schools_map_with_catchments.html')
print(f"Map saved as 'schools_map_with_catchments.html'")
print(f"\n🏫 Schools potentially in catchment from N16 7RJ:")
if schools_in_catchment:
    for school in schools_in_catchment[:10]:  # Show top 10 closest
        print(f"  - {school['name']} ({school['rating']}): {school['distance']}m away, estimated catchment {school['catchment']}m")
else:
    print("  No schools found within their estimated catchment areas")

print("\n📝 Note: Toggle 'Catchment Areas' layer on/off using the control in the top right of the map")
print("⚠️  Actual catchment areas vary yearly based on applications. Check with local authorities for accurate data.")