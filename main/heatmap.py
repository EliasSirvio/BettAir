import matplotlib.pyplot as plt
import numpy as np
from map import Map, Station
from fuzzy_utils import run_simulation, generate_random_stations
from tqdm import tqdm
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define map size and number of stations
MAP_SIZE, N_STATIONS = 100, 9  # Adjust based on your coordinate system and data

# Example list of real location IDs from OpenAQ
real_location_ids = [3057947, 225719, 3057946, 3057945, 3057948, 225713, 225723, 155, 225848]  # Replace with actual location IDs

# Initialize Station objects with real data
stations = []
for loc_id in real_location_ids[:N_STATIONS]:
    population_density = random.randint(1, 10)  # Replace with actual data if available
    veg_cover = random.randint(1, 5)            # Replace with actual data if available
    try:
        # Remove the 'map_size' keyword argument
        station = Station(location_id=loc_id, population_density=population_density, veg_cover=veg_cover)
        stations.append(station)
    except Exception as e:
        print(f"Error initializing Station with ID {loc_id}: {e}")
        # Optionally, skip this station or assign default values

# Convert stations list to NumPy array
stations_array = np.array(stations)

# Initialize Map object
map_obj = Map(stations_array, size=MAP_SIZE, verbose=True)

# Initialize heatmap array
heatmap = np.empty((map_obj.size, map_obj.size))

# Iterate over each grid point to compute 'need_for_action'
for i in tqdm(range(map_obj.size), desc="Processing rows"):
    for j in range(map_obj.size):
        # Map grid indices to float coordinates
        # Assuming each grid cell represents 1 unit; adjust as needed
        query_location = (i + 0.5, j + 0.5)  # Center of the grid cell
        heatmap[i, j] = run_simulation(query_location, map_obj)

# Plot heatmap
plt.figure(figsize=(10, 8))
plt.imshow(
    heatmap, 
    cmap='hot', 
    interpolation='bicubic', 
    origin='lower', 
    extent=(map_obj.min_lat, map_obj.max_lat, map_obj.min_lon, map_obj.max_lon)
)
plt.colorbar(label='Need for Action (%)')
plt.title('Need for Green Areas', pad=10)
plt.xlabel("Latitude")
plt.ylabel("Longitude")

# Plot station locations
plt.scatter(
    [station.latitude for station in stations],
    [station.longitude for station in stations],
    color='g', 
    marker='o', 
    label="Stations",
    edgecolors='black'
)

plt.legend()
plt.show()
