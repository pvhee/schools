import pandas as pd
import folium
from folium import plugins

# Read the CSV data with Ofsted ratings
df = pd.read_csv('schools_ofsted_london_with_ratings.csv')

# Create a map centered around the average of all school coordinates
center_lat = df['Latitude'].mean()
center_lon = df['Longitude'].mean()

# Create the map
m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

# Add home location marker (N16 7RJ)
home_lat = 51.5645
home_lon = -0.0759
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
).add_to(m)

# Define colors for Ofsted ratings
rating_colors = {
    'Outstanding': 'green',
    'Good': 'blue',
    'Requires Improvement': 'orange',
    'Inadequate': 'red',
    'Not judged': 'gray',
    'nan': 'lightgray'  # For schools without ratings
}

# Add school markers with color-coded ratings
for idx, row in df.iterrows():
    # Get the rating and color
    rating = str(row['Ofsted Rating']) if pd.notna(row['Ofsted Rating']) else 'No rating'
    color = rating_colors.get(row['Ofsted Rating'], 'lightgray')
    
    # Create popup text with school info
    popup_text = f"""
    <b>{row['EstablishmentName']}</b><br>
    URN: {row['URN']}<br>
    <b>Ofsted Rating: {rating}</b>
    """
    
    # Add inspection date if available
    if pd.notna(row['Inspection start date']):
        popup_text += f"<br>Last Inspection: {row['Inspection start date']}"
    
    # Add marker for each school
    folium.Marker(
        [row['Latitude'], row['Longitude']],
        popup=folium.Popup(popup_text, max_width=300),
        tooltip=f"{row['EstablishmentName']} - {rating}",
        icon=folium.Icon(color=color, icon='graduation-cap', prefix='fa')
    ).add_to(m)

# Add a legend
legend_html = '''
<div style="position: fixed; 
            bottom: 50px; right: 50px; width: 200px; height: auto; 
            background-color: white; z-index:9999; font-size:14px;
            border:2px solid grey; border-radius:5px; padding: 10px">
<h4 style="margin: 0;">Ofsted Ratings</h4>
<p style="margin: 5px;"><i class="fa fa-graduation-cap" style="color:green;"></i> Outstanding</p>
<p style="margin: 5px;"><i class="fa fa-graduation-cap" style="color:blue;"></i> Good</p>
<p style="margin: 5px;"><i class="fa fa-graduation-cap" style="color:orange;"></i> Requires Improvement</p>
<p style="margin: 5px;"><i class="fa fa-graduation-cap" style="color:red;"></i> Inadequate</p>
<p style="margin: 5px;"><i class="fa fa-graduation-cap" style="color:gray;"></i> Not Judged</p>
<p style="margin: 5px;"><i class="fa fa-graduation-cap" style="color:lightgray;"></i> No Rating</p>
<p style="margin: 5px;"><i class="fa fa-home" style="color:red;"></i> Home Location</p>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Add fullscreen button
plugins.Fullscreen().add_to(m)

# Calculate statistics
total_schools = len(df)
with_rating = df['Ofsted Rating'].notna().sum()
outstanding = (df['Ofsted Rating'] == 'Outstanding').sum()
good = (df['Ofsted Rating'] == 'Good').sum()
requires_improvement = (df['Ofsted Rating'] == 'Requires Improvement').sum()
inadequate = (df['Ofsted Rating'] == 'Inadequate').sum()

# Save the map
m.save('schools_map_with_ofsted.html')
print(f"Map saved as 'schools_map_with_ofsted.html'")
print(f"\n📊 Statistics:")
print(f"Total schools: {total_schools}")
print(f"Schools with Ofsted ratings: {with_rating}")
print(f"  - Outstanding: {outstanding}")
print(f"  - Good: {good}")
print(f"  - Requires Improvement: {requires_improvement}")
print(f"  - Inadequate: {inadequate}")
print("Open the file in your browser to view the interactive map with color-coded Ofsted ratings")