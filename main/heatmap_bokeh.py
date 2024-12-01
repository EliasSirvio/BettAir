import numpy as np
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColorBar, LinearColorMapper, BasicTicker, HoverTool, ColumnDataSource, LabelSet
from bokeh.transform import transform
from map import Map, Station
from fuzzy_utils import run_simulation
from tqdm import tqdm
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define map size and number of stations
MAP_SIZE, N_STATIONS = 100, 14  # Adjust based on your coordinate system and data

# Example list of real location IDs from OpenAQ
real_location_ids = [3057947, 225719, 3057946, 3057945, 3057948, 225713, 225723, 155, 225848, 225767, 225802, 1235983, 3079185, 225755]  # Replace with actual location IDs

# Initialize Station objects with real data
stations = []
for loc_id in real_location_ids[:N_STATIONS]:
    population_density = random.randint(1, 10)  # Replace with actual data if available
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
heatmap = np.empty((map_obj.size, map_obj.size))

# Iterate over each grid point to compute 'need_for_action'
for i in tqdm(range(map_obj.size), desc="Processing rows"):
    for j in range(map_obj.size):
        # Map grid indices to float coordinates
        # To center the query within the cell, add 0.5
        query_location = (i + 0.5, j + 0.5)  # Center of the grid cell
        heatmap[i, j] = run_simulation(query_location, map_obj)

# Optionally, flip the heatmap vertically to align with geographic coordinates
heatmap = np.flipud(heatmap)

# Prepare data for Bokeh
output_file("need_for_action_heatmap.html")

# Define the range for the heatmap
x_min, x_max = map_obj.min_lat, map_obj.max_lat
y_min, y_max = map_obj.min_lon, map_obj.max_lon

# Create a figure
try:
    p = figure(
        title="Need for Green Areas",
        x_range=(x_min, x_max), 
        y_range=(y_min, y_max),
        tools="pan,wheel_zoom,reset,hover,save",
        toolbar_location="above",
        width=800, 
        height=600
    )
except TypeError as te:
    logging.error(f"TypeError while creating figure: {te}")
    # Attempting workaround if 'plot_width' and 'plot_height' are invalid
    p = figure(
        title="Need for Green Areas",
        x_range=(x_min, x_max), 
        y_range=(y_min, y_max),
        tools="pan,wheel_zoom,reset,hover,save",
        toolbar_location="above",
        width=800,      # Using 'width' instead
        height=600      # Using 'height' instead
    )

# Define a color mapper
color_mapper = LinearColorMapper(palette="Viridis256", low=np.min(heatmap), high=np.max(heatmap))

# Add the heatmap image
p.image(
    image=[heatmap],
    x=x_min,
    y=y_min,
    dw=(x_max - x_min),
    dh=(y_max - y_min),
    color_mapper=color_mapper,
    level="image"
)

# Add color bar
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

# Extract 'need_for_action' at station locations
def get_need_for_action_at_station(station, heatmap, map_obj):
    """
    Retrieves the 'need_for_action' value from the heatmap at the station's geographic location.
    """
    # Calculate the relative position within the heatmap grid
    rel_x = (station.latitude - map_obj.min_lat) / (map_obj.max_lat - map_obj.min_lat)
    rel_y = (station.longitude - map_obj.min_lon) / (map_obj.max_lon - map_obj.min_lon)
    
    # Map to heatmap indices
    i = int(rel_x * (map_obj.size - 1))
    j = int(rel_y * (map_obj.size - 1))
    
    # Ensure indices are within bounds
    i = min(max(i, 0), map_obj.size - 1)
    j = min(max(j, 0), map_obj.size - 1)
    
    # Since we flipped the heatmap, adjust the y-index
    j_flipped = map_obj.size - 1 - j
    
    return heatmap[j_flipped, i]
    
station_need_action = []
for station in stations:
    naq = get_need_for_action_at_station(station, heatmap, map_obj)
    station_need_action.append(naq)

source = ColumnDataSource(data=dict(
    latitude=station_latitudes,
    longitude=station_longitudes,
    air_quality=station_aq,
    population_density=station_pd,
    vegetation_cover=station_vc,
    need_for_action=station_need_action
))

station_renderer = p.scatter('latitude', 'longitude', size=10, fill_color="green", 
                             fill_alpha=0.6, line_color="black", legend_label="Stations",
                             source=source)



# Customize the hover tool for stations
hover = HoverTool(
    tooltips=[
        ("Latitude", "@latitude"),
        ("Longitude", "@longitude"),
        ("Air Quality (PM2.5)", "@air_quality"),
        ("Population Density", "@population_density"),
        ("Vegetation Cover", "@vegetation_cover"),
        ("Need for Action", "@need_for_action")
    ],
    renderers=[station_renderer]  # Ensure hover applies only to stations
)

p.add_tools(hover)


# Add LabelSet for 'Need for Action'
labels = LabelSet(
    x='latitude',
    y='longitude',
    text='need_for_action',
    level='glyph',
    x_offset=5,
    y_offset=5,
    source=source,
    render_mode='canvas',  # Valid in Bokeh 3.4.0+
    text_font_size="10pt",
    text_color="white",
    background_fill_color="black",
    background_fill_alpha=0.6
)

p.add_layout(labels)

# Show the plot
show(p)