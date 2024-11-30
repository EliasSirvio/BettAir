import numpy as np
from scipy.spatial import cKDTree
from openaq_api import get_air_quality_and_coordinates
from scipy.interpolate import Rbf  # Optional for advanced interpolation


class Station:
    def __init__(self, location_id: int, population_density: int, veg_cover: int) -> None:
        """
        Initialize a Station with real geographic coordinates.
        
        Parameters:
        - location_id (int): OpenAQ location ID.
        - population_density (int): Population density (inhabitants/ha).
        - veg_cover (int): Vegetation cover (%).
        """
        air_quality, coordinates = get_air_quality_and_coordinates(location_id)
        
        if coordinates:
            self.latitude = coordinates['latitude']
            self.longitude = coordinates['longitude']
            self.location = (self.latitude, self.longitude)  # Real coordinates as floats
        else:
            self.latitude = 0.0
            self.longitude = 0.0
            self.location = (self.latitude, self.longitude)  # Default coordinates
        
        self.data = np.array([
            air_quality if air_quality is not None else -1,  # Air Quality (µg/m³)
            population_density,                             # Population Density (inhabitants/ha)
            veg_cover                                       # Vegetation Cover (%)
        ])
    
    def __str__(self) -> str:
        aq, pd, vc = self.data
        return f"""
    Station at ({self.latitude:.4f}, {self.longitude:.4f}):
        Air Quality =           {aq}
        Population Density =    {pd}
        Vegetation Cover =      {vc}
        """



class Map:
    def __init__(self, stations: np.ndarray, size: int=100, verbose: bool=False) -> None:
        """
        Initialize the Map with a set of stations.
        
        Parameters:
        - stations (np.ndarray): Array of Station objects.
        - size (int): Size of the heatmap grid (default 100).
        - verbose (bool): Enable verbose output.
        """
        self.size = size
        self.verbose = verbose
        
        # Extract real coordinates from stations
        real_coordinates = np.array([[station.latitude, station.longitude] for station in stations])
        self.data = np.array([station.data for station in stations])  # Shape: (n_stations, 3)
        
        # Determine min and max for normalization
        self.min_lat = real_coordinates[:,0].min()
        self.max_lat = real_coordinates[:,0].max()
        self.min_lon = real_coordinates[:,1].min()
        self.max_lon = real_coordinates[:,1].max()
        
        if self.verbose:
            print(f"Latitude range: {self.min_lat} to {self.max_lat}")
            print(f"Longitude range: {self.min_lon} to {self.max_lon}")
        
        # Normalize coordinates to [0, size)
        self.normalized_coordinates = np.zeros_like(real_coordinates, dtype=float)
        self.normalized_coordinates[:,0] = (real_coordinates[:,0] - self.min_lat) / (self.max_lat - self.min_lat) * (size - 1)
        self.normalized_coordinates[:,1] = (real_coordinates[:,1] - self.min_lon) / (self.max_lon - self.min_lon) * (size - 1)
        
        if self.verbose:
            print(f"Normalized coordinates:\n{self.normalized_coordinates}")
        
        # Build KD-Tree for efficient spatial queries
        self.kd_tree = cKDTree(self.normalized_coordinates)
    
    def __str__(self) -> str:
        return f"Map contains {len(self.normalized_coordinates)} stations."
    
    def add_station(self, station: Station) -> None:
        """
        Add a single Station to the Map.
        
        Parameters:
        - station (Station): The Station object to add.
        """
        # Update min and max
        self.min_lat = min(self.min_lat, station.latitude)
        self.max_lat = max(self.max_lat, station.latitude)
        self.min_lon = min(self.min_lon, station.longitude)
        self.max_lon = max(self.max_lon, station.longitude)
        
        # Normalize new station's coordinates
        normalized_lat = (station.latitude - self.min_lat) / (self.max_lat - self.min_lat) * (self.size - 1)
        normalized_lon = (station.longitude - self.min_lon) / (self.max_lon - self.min_lon) * (self.size - 1)
        normalized_location = (normalized_lat, normalized_lon)
        
        # Append to existing data
        self.normalized_coordinates = np.vstack([self.normalized_coordinates, normalized_location])
        self.data = np.vstack([self.data, station.data])
        self.kd_tree = cKDTree(self.normalized_coordinates)  # Rebuild KD-Tree
        
        if self.verbose:
            print(f"Added Station at ({station.latitude:.4f}, {station.longitude:.4f}) normalized to ({normalized_lat:.2f}, {normalized_lon:.2f}).")
    
    def get_data(self, location: tuple[float, float], n_neighbors: int=3) -> tuple[float, int, int]:
        """
        Interpolate data for a given location using the n closest stations with Inverse Distance Weighting (IDW).
        
        Parameters:
        - location (tuple[float, float]): The (x, y) location on the map grid (float-based).
        - n_neighbors (int): Number of nearest neighbors to consider for interpolation.
        
        Returns:
        - tuple[float, int, int]: Interpolated (air_quality, population_density, veg_cover)
        """
        # Query KD-Tree for nearest neighbors
        distances, indices = self.kd_tree.query(location, k=n_neighbors)
        
        # Handle case when only one neighbor is found
        if n_neighbors == 1:
            indices = [indices]
            distances = [distances]
        
        # Check if any station is exactly at the query location
        exact_match = np.isclose(distances, 0)
        if any(exact_match):
            matched_index = indices[exact_match][0]
            return tuple(self.data[matched_index])
        
        # Compute weights using Inverse Distance Weighting (IDW)
        weights = 1 / (distances ** 2 + 1e-6)  # Adding a small value to prevent division by zero
        weighted_data = self.data[indices].T * weights
        weighted_sum = np.sum(weighted_data, axis=1)
        sum_weights = np.sum(weights)
        interpolated = weighted_sum / sum_weights
        
        return tuple(interpolated)

def barycentric_coordinates(triangle: np.ndarray, point: tuple[float, float]):
    """
    Calculate the barycentric coordinates of a point with respect to a triangle.
    
    Parameters:
    triangle : array-like, shape (3, 2)
        The vertices of the triangle.
    point : tuple[float, float]
        The point for which to calculate the barycentric coordinates.
    
    Returns:
    array, shape (3,)
        The barycentric coordinates of the point.
    """
    triangle = np.array(triangle)
    assert triangle.shape == (3, 2), f"Triangle had wrong shape! It should have shape (3,2) but had shape {triangle.shape}."

    T = np.vstack((triangle.T, np.ones((1, 3))))
    v = np.append(point, 1)
    try:
        return np.linalg.solve(T, v)
    except np.linalg.LinAlgError:
        raise ValueError("Triangle vertices are not linearly independent!")
