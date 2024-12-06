import matplotlib.pyplot as plt
import numpy as np
from map import Map
from heatmap_utils import run_simulation, generate_random_stations
from tqdm import tqdm

if __name__ == "__main__":
    # Size of map, and number of stations on the map
    MAP_SIZE, N_STATIONS = 50, 50
    # NB: Significantly affects computation time - Output is computed for MAP_SIZE^2 locations

# Initiate map
stations = generate_random_stations(n_stations=N_STATIONS, map_size=MAP_SIZE)
map = Map(stations, size=MAP_SIZE)

# Compute heatmap
heatmap = np.empty((map.size, map.size))
for i in tqdm(range(map.size)):
    for j in range(map.size):
        heatmap[i,j] = run_simulation((i,j), map=map)

# Plot heatmap figure
plt.imshow(heatmap, cmap='hot', interpolation='bicubic')
plt.colorbar(label='Need for action')
plt.title('Need for green areas', pad=10)
plt.xlabel("West <----> East")
plt.ylabel("South <----> North")
plt.scatter([x for x,y in map.data.keys()], [y for x,y in map.data.keys()], color='g', marker='o', label="Stations")
plt.legend()
plt.show()