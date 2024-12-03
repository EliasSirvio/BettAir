import matplotlib.pyplot as plt
import numpy as np
from map import Map
from heatmap_utils import run_simulation, generate_random_stations, plot_heatmap
from tqdm import tqdm

if __name__ == "__main__":
    # Size of map, and number of stations on the map
    MAP_SIZE, N_STATIONS = 30, 100
    # NB: Significantly affects computation time - Output is computed for MAP_SIZE^2 locations

    # Initiate map
    stations = generate_random_stations(n_stations=N_STATIONS, map_size=MAP_SIZE)
    map = Map(stations, size=MAP_SIZE)

    # Compute heatmap
    heatmap = np.empty((map.size, map.size))
    for i in tqdm(range(map.size)):
        for j in range(map.size):
            heatmap[i,j] = run_simulation((i,j), map=map)

    plot_heatmap(heatmap, map)