import pandas as pd
import folium
from folium import plugins

# Read the CSV data
df = pd.read_csv('schools_ofsted_london.csv')

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

# Add school markers
for idx, row in df.iterrows():
    # Create popup text with school info
    popup_text = f"""
    <b>{row['EstablishmentName']}</b><br>
    URN: {row['URN']}
    """
    
    # Add marker for each school
    folium.Marker(
        [row['Latitude'], row['Longitude']],
        popup=folium.Popup(popup_text, max_width=300),
        tooltip=row['EstablishmentName'],
        icon=folium.Icon(color='blue', icon='graduation-cap', prefix='fa')
    ).add_to(m)

# Add marker cluster for better visualization when zoomed out
marker_cluster = plugins.MarkerCluster().add_to(m)

for idx, row in df.iterrows():
    folium.Marker(
        [row['Latitude'], row['Longitude']],
        popup=f"{row['EstablishmentName']}",
        tooltip=row['EstablishmentName']
    ).add_to(marker_cluster)

# Add fullscreen button
plugins.Fullscreen().add_to(m)

# Save the map
m.save('schools_map.html')
print(f"Map saved as 'schools_map.html' - {len(df)} schools plotted")
print("Open the file in your browser to view the interactive map")