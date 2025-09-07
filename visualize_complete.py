import pandas as pd
import folium
from folium import plugins
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import json

# Read the complete school data with GCSE/Progress 8 data
df = pd.read_csv('schools_london_complete.csv')

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

# Define colors based on Progress 8 scores
def get_school_color(row):
    """Get school color based on Progress 8 performance"""
    if pd.isna(row['diffn_p8mea']):
        return 'lightgray'  # No Progress 8 data
    
    p8_score = row['diffn_p8mea']
    
    if p8_score >= 1.0:
        return 'purple'      # Well above average (excellent)
    elif p8_score >= 0.5:
        return 'green'       # Above average
    elif p8_score >= -0.5:
        return 'blue'        # Average
    elif p8_score >= -1.0:
        return 'orange'      # Below average
    else:
        return 'red'         # Well below average

# Create feature groups for different elements
school_markers = folium.FeatureGroup(name='Schools', show=True)
high_performing = folium.FeatureGroup(name='High Progress 8 (>1.0)', show=True)

# Add school markers with comprehensive information
for idx, row in df.iterrows():
    # Calculate distance from home
    school_loc = (row['Latitude'], row['Longitude'])
    home_loc = (home_lat, home_lon)
    distance_meters = geodesic(home_loc, school_loc).meters
    distance_miles = geodesic(home_loc, school_loc).miles
    
    # Get the rating and color
    rating = str(row['Ofsted Rating']) if pd.notna(row['Ofsted Rating']) else 'No rating'
    color = get_school_color(row)
    
    # Create comprehensive popup text
    popup_text = f"""
    <b>{row['EstablishmentName']}</b><br>
    <b>📍 Distance from home: {distance_meters:.0f}m ({distance_miles:.1f} miles)</b><br>
    URN: {row['URN']}<br>
    <b>Ofsted Rating: {rating}</b><br>
    """
    
    # Add Progress 8 information if available
    if pd.notna(row['diffn_p8mea']):
        p8_score = row['diffn_p8mea']
        p8_band = row['p8_banding']
        popup_text += f"<b>📊 Progress 8: {p8_score:+.2f} ({p8_band})</b><br>"
    else:
        popup_text += "<i>Progress 8: No data available</i><br>"
    
    # Add Attainment 8 if available
    if pd.notna(row['diffn_att8']):
        popup_text += f"<b>📈 Attainment 8: {row['diffn_att8']:+.1f}</b><br>"
    
    # Add inspection date if available
    if pd.notna(row['Inspection start date']):
        popup_text += f"<br>Last Inspection: {row['Inspection start date']}"
    
    # Create tooltip text
    tooltip_parts = [row['EstablishmentName'], rating]
    if pd.notna(row['diffn_p8mea']):
        tooltip_parts.append(f"P8: {row['diffn_p8mea']:+.2f}")
    tooltip_parts.append(f"{distance_meters:.0f}m")
    tooltip_text = " | ".join(tooltip_parts)
    
    # Choose icon based on performance
    if pd.notna(row['diffn_p8mea']) and row['diffn_p8mea'] > 1.0:
        icon = folium.Icon(color=color, icon='star', prefix='fa')
        target_group = high_performing
    else:
        icon = folium.Icon(color=color, icon='graduation-cap', prefix='fa')
        target_group = school_markers
    
    # Add marker
    folium.Marker(
        [row['Latitude'], row['Longitude']],
        popup=folium.Popup(popup_text, max_width=350),
        tooltip=tooltip_text,
        icon=icon
    ).add_to(target_group)

# Add feature groups to map
school_markers.add_to(m)
high_performing.add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

# Enhanced legend
legend_html = '''
<div style="position: fixed; 
            bottom: 50px; right: 50px; width: 300px; height: auto; 
            background-color: white; z-index:9999; font-size:14px;
            border:2px solid grey; border-radius:5px; padding: 10px">
<h4 style="margin: 0;">GCSE Progress 8 Performance</h4>
<hr>
<h5>Progress 8 Color Coding:</h5>
<p style="margin: 3px;"><i class="fa fa-star" style="color:purple;"></i> Excellent (+1.0 and above)</p>
<p style="margin: 3px;"><i class="fa fa-graduation-cap" style="color:green;"></i> Above Average (+0.5 to +1.0)</p>
<p style="margin: 3px;"><i class="fa fa-graduation-cap" style="color:blue;"></i> Average (-0.5 to +0.5)</p>
<p style="margin: 3px;"><i class="fa fa-graduation-cap" style="color:orange;"></i> Below Average (-1.0 to -0.5)</p>
<p style="margin: 3px;"><i class="fa fa-graduation-cap" style="color:red;"></i> Well Below Average (-1.0 and below)</p>
<p style="margin: 3px;"><i class="fa fa-graduation-cap" style="color:lightgray;"></i> No Progress 8 Data</p>
<hr>
<h5>What is Progress 8?</h5>
<p style="margin: 2px; font-size:12px;">Measures how much progress students make from KS2 to GCSE compared to similar students nationally</p>
<p style="margin: 2px; font-size:12px;">0 = Average progress</p>
<p style="margin: 2px; font-size:12px;">+1.0 = Students make 1 grade more progress than average</p>
<hr>
<p style="margin: 3px;"><i class="fa fa-home" style="color:red;"></i> Home (N16 7RJ)</p>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Add fullscreen button
plugins.Fullscreen().add_to(m)

# Save the map
m.save('schools_complete_map.html')
print(f"Complete map saved as 'schools_complete_map.html'")

# Show nearby schools with GCSE data
print(f"\n🏆 Top 10 nearby schools by Progress 8 score:")
nearby_with_p8 = []
for idx, row in df.iterrows():
    if pd.notna(row['diffn_p8mea']):
        school_loc = (row['Latitude'], row['Longitude'])
        home_loc = (home_lat, home_lon)
        distance = geodesic(home_loc, school_loc).meters
        
        nearby_with_p8.append({
            'name': row['EstablishmentName'],
            'distance': distance,
            'p8_score': row['diffn_p8mea'],
            'p8_band': row['p8_banding'],
            'ofsted': row['Ofsted Rating']
        })

# Sort by Progress 8 score (descending) and limit to schools within 5km
nearby_with_p8.sort(key=lambda x: x['p8_score'], reverse=True)
nearby_schools = [s for s in nearby_with_p8 if s['distance'] <= 5000][:10]

for i, school in enumerate(nearby_schools, 1):
    print(f"{i}. {school['name']}")
    print(f"   📊 Progress 8: {school['p8_score']:+.2f} ({school['p8_band']})")
    print(f"   🎓 Ofsted: {school['ofsted']}")
    print(f"   📍 Distance: {school['distance']:.0f}m")
    print()

print(f"📈 Schools with GCSE data: {(df['diffn_p8mea'].notna()).sum()} out of {len(df)}")
print("💫 Purple star markers indicate schools with excellent Progress 8 scores (>+1.0)")