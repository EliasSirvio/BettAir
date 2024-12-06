import numpy as np
from bokeh.plotting import gmap, show, output_file
from bokeh.models import (
    ColorBar, LinearColorMapper, BasicTicker, HoverTool,
    ColumnDataSource, LabelSet, GMapOptions
)
from mapApi import Map, Station
from heatmap_utils_api import (run_simulation,
    get_air_pollution_label,
    get_population_density_label,
    get_veg_cover_label,
    get_need_for_action_label)
from tqdm import tqdm
import random
import logging
import os
import matplotlib.pyplot as plt


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define map size and number of stations
MAP_SIZE, N_STATIONS = 100, 14  # Adjust based on your coordinate system and data

# List of location ids in London 14
real_location_ids = [
    3057947, 225719, 3057946, 3057945, 3057948,
    225713, 225723, 155, 225848, 225767,
    225802, 1235983, 3079185, 225755
]  
# list of location ids in Belgrade 6
""""
real_location_ids = [
    1541052, 11587, 784135, 10837, 784137, 11588
] """

# Initialize Station objects with real data
stations = []
for loc_id in real_location_ids[:N_STATIONS]:
    population_density = random.randint(10, 80)  # Replace with actual data if available
    veg_cover = random.randint(1, 5)            # Replace with actual data if available
    try:
        station = Station(location_id=loc_id, population_density=population_density, veg_cover=veg_cover)
        stations.append(station)
        print(f"Successfully added Station ID {loc_id}")
    except Exception as e:
        logging.error(f"Error initializing Station with ID {loc_id}: {e}")
        # Optionally, skip this station or assign default values

# Convert stations list to NumPy array
stations_array = np.array(stations)

# Debugging statement to check the shape and contents
print(f"stations_array shape: {stations_array.shape}")
print(f"stations_array contents: {stations_array}")

# Initialize Map object
try:
    map_obj = Map(stations_array, size=MAP_SIZE, verbose=True)
    print("Map object initialized successfully.")
except Exception as e:
    logging.error(f"Error initializing Map object: {e}")
    exit(1)  # Exit if Map initialization fails

# Initialize heatmap array
# Correct assignments for x_min, x_max, y_min, y_max
x_min, x_max = map_obj.min_lon, map_obj.max_lon  # Longitude
y_min, y_max = map_obj.min_lat, map_obj.max_lat  # Latitude

# Correct average latitude and longitude
average_lat = (y_min + y_max) / 2
average_lon = (x_min + x_max) / 2

print(f"Map Longitude Range: min_lon = {map_obj.min_lon}, max_lon = {map_obj.max_lon}")
print(f"Map Latitude Range: min_lat = {map_obj.min_lat}, max_lat = {map_obj.max_lat}")

# Heatmap generation loop
heatmap = np.empty((map_obj.size, map_obj.size))

for i in tqdm(range(map_obj.size), desc="Processing columns (longitude)"):
    for j in range(map_obj.size):
        # Calculate fractions along the grid
        fraction_x = (i + 0.5) / map_obj.size  # Longitude fraction
        fraction_y = (j + 0.5) / map_obj.size  # Latitude fraction

        # Map fractions to actual longitude and latitude
        longitude = x_min + fraction_x * (x_max - x_min)
        latitude = y_min + fraction_y * (y_max - y_min)

        query_location = (latitude, longitude)  # Use (latitude, longitude)
        heatmap[j, i] = run_simulation(query_location, map_obj)

# Transpose the heatmap to match x and y axes
#heatmap = heatmap.T

# Optionally, flip the heatmap vertically to align with geographic coordinates
#heatmap = np.flipud(heatmap)


# Prepare data for Bokeh
output_file("need_for_action_heatmap.html")

# Google Maps API Key (Replace with your actual API key)
API_KEY = ""

# Define map options using GMapOptions
average_lat = (y_min + y_max) / 2
average_lon = (x_min + x_max) / 2
map_options = GMapOptions(lat=average_lat, lng=average_lon, map_type="roadmap", zoom=12)

# Create a GMap plot
p = gmap(
    API_KEY,
    map_options,
    title="Need for Green Areas",
    tools="pan,wheel_zoom,reset,hover,save",
    toolbar_location="above",
    width=800,
    height=600
)

# Define a color mapper for the heatmap
low_percentile = np.percentile(heatmap, 5)   # 5th percentile
high_percentile = np.percentile(heatmap, 95) # 95th percentile
print(f"5th Percentile: {low_percentile}, 95th Percentile: {high_percentile}")
color_mapper = LinearColorMapper(palette="Inferno256", low=low_percentile, high=high_percentile)

# Add the heatmap image to the map
# The 'image' glyph expects a 2D array and will overlay it on the map

p.image(
    image=[heatmap],
    x=x_min,
    y=y_min,
    dw=(x_max - x_min),
    dh=(y_max - y_min),
    color_mapper=color_mapper,
    level="image",
    alpha=0.6  # Adjust transparency as needed
)


# Add a color bar to interpret the heatmap colors
color_bar = ColorBar(
    color_mapper=color_mapper,
    ticker=BasicTicker(desired_num_ticks=10),
    label_standoff=12,
    border_line_color=None,
    location=(0,0)
)
p.add_layout(color_bar, 'right')

# Prepare station data
station_latitudes = [station.latitude for station in stations]
station_longitudes = [station.longitude for station in stations]
station_aq = [station.data[0] for station in stations]
station_pd = [station.data[1] for station in stations]
station_vc = [station.data[2] for station in stations]

def get_need_for_action_at_station(station, heatmap, map_obj):
    """
    Retrieves the 'need_for_action' value from the heatmap at the station's geographic location.
    """
    # Calculate the relative position within the heatmap grid
    rel_x = (station.longitude - map_obj.min_lon) / (map_obj.max_lon - map_obj.min_lon) if (map_obj.max_lon - map_obj.min_lon) != 0 else 0.5
    rel_y = (station.latitude - map_obj.min_lat) / (map_obj.max_lat - map_obj.min_lat) if (map_obj.max_lat - map_obj.min_lat) != 0 else 0.5
    
    # Clamp relative positions to [0, 1]
    rel_x = min(max(rel_x, 0), 1)
    rel_y = min(max(rel_y, 0), 1)
    
    # Map to heatmap indices
    i = int(rel_x * (map_obj.size - 1))
    j = int(rel_y * (map_obj.size - 1))
    
    # Ensure indices are within bounds
    i = min(max(i, 0), map_obj.size - 1)
    j = min(max(j, 0), map_obj.size - 1)
    
    # Adjust the indices if you flipped or transposed the heatmap
    # If you transposed the heatmap, swap i and j
    return heatmap[j, i]


# Extract 'need_for_action' for each station
station_need_action = [get_need_for_action_at_station(station, heatmap, map_obj) for station in stations]

# Extract numerical values for each station
station_aq = [station.data[0] for station in stations]
station_pd = [station.data[1] for station in stations]
station_vc = [station.data[2] for station in stations]

# Compute fuzzy labels for each variable
station_aq_labels = [get_air_pollution_label(value) for value in station_aq]
station_pd_labels = [get_population_density_label(value) for value in station_pd]
station_vc_labels = [get_veg_cover_label(value) for value in station_vc]

# Extract 'need_for_action' for each station
station_need_action = [get_need_for_action_at_station(station, heatmap, map_obj) for station in stations]
station_need_action_labels = [get_need_for_action_label(value) for value in station_need_action]

# Update ColumnDataSource to include 'need_for_action'
source = ColumnDataSource(data=dict(
    latitude=station_latitudes,
    longitude=station_longitudes,
    air_quality=station_aq,
    air_quality_label=station_aq_labels,
    population_density=station_pd,
    population_density_label=station_pd_labels,
    vegetation_cover=station_vc,
    vegetation_cover_label=station_vc_labels,
    need_for_action=station_need_action,
    need_for_action_label=station_need_action_labels
))

# Add station markers using 'scatter()' instead of deprecated 'circle()'
station_renderer = p.scatter(
    'longitude', 'latitude',  # In GMap, x corresponds to longitude and y to latitude
    size=10,
    fill_color="green",
    fill_alpha=0.6,
    line_color="black",
    legend_label="Stations",
    source=source
)

# Customize the hover tool for stations
hover = HoverTool(
    tooltips=[
        ("Latitude", "@latitude"),
        ("Longitude", "@longitude"),
        ("Air Quality (PM2.5)", "@air_quality (@air_quality_label)"),
        ("Population Density", "@population_density (@population_density_label)"),
        ("Vegetation Cover", "@vegetation_cover (@vegetation_cover_label)"),
        ("Need for Action", "@need_for_action (@need_for_action_label)")
    ],
    renderers=[station_renderer]  # Ensure hover applies only to stations
)

p.add_tools(hover)

# Add LabelSet for 'Need for Action'
labels = LabelSet(
    x='longitude',  # x corresponds to longitude in GMap
    y='latitude',   # y corresponds to latitude in GMap
    text='need_for_action',
    level='glyph',
    x_offset=5,
    y_offset=5,
    source=source,
    #render_mode='canvas', 
    text_font_size="10pt",
    text_color="white",
    background_fill_color="black",
    background_fill_alpha=0.6
)

p.add_layout(labels)

# Show the plot
show(p)

#debug
print("Heatmap statistics:")
print(f"Min: {np.min(heatmap)}, Max: {np.max(heatmap)}, Mean: {np.mean(heatmap)}")
print(f"Any NaN values: {np.isnan(heatmap).any()}")
print(f"Any Inf values: {np.isinf(heatmap).any()}")

print(f"Heatmap Overlay Parameters:")
print(f"x_min (Longitude): {x_min}, x_max (Longitude): {x_max}")
print(f"y_min (Latitude): {y_min}, y_max (Latitude): {y_max}")

print("Sample Heatmap Values:")
print(heatmap[:5, :5])  # Print a small section of the heatmap

plt.figure(figsize=(8, 6))
plt.imshow(heatmap, extent=[x_min, x_max, y_min, y_max], origin='lower', cmap='inferno')
plt.colorbar(label='Need for Action')
plt.scatter(station_longitudes, station_latitudes, c='green', marker='o')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Heatmap Verification')
plt.show()

for station in stations:
    print(f"Station ID: {station.location_id}, Latitude: {station.latitude}, Longitude: {station.longitude}")

try:
    station = Station(location_id=loc_id, population_density=population_density, veg_cover=veg_cover)
    print(f"Station {loc_id} - Latitude: {station.latitude}, Longitude: {station.longitude}")
    stations.append(station)
except Exception as e:
    logging.error(f"Error initializing Station with ID {loc_id}: {e}")

for station in stations:
    print(f"Station ID: {station.location_id}, Air Quality (PM2.5): {station.data[0]}")
