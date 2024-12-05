import numpy as np
from scipy.spatial import cKDTree
from map_utils import linearly_independent, barycentric_coordinates

class Station:
    def __init__(self, location: tuple[int, int], air_quality: float, population_density: float, veg_cover: float) -> None:
        self.location = location
        self.data = np.array([air_quality, population_density, veg_cover])

    def __str__(self) -> str:
        aq, pd, vc = self.data
        return f"""
    Station at {self.location}:
        Air Quality =           {aq}
        Population Density =    {pd}
        Vegetation Cover =      {vc}
        """

class Map:
    def __init__(self, stations: np.array, size: int=100, verbose=False) -> None:
        """
        Map keeping data from sensor stations at certain locations on a 2D-grid.
        Can interpolate data from surrounding stations to get data for any point on the map 

        Parameters:
            stations:
                Array of stations that are located on the map.
            size:
                Length of the sides of the map. The map is square-shaped.
            verbose:
                Set to True to make the map print its processing to the terminal
        """
        self.size = size
        self.stations = np.empty((0))
        self.data = {}
        self.add_stations(stations) # Fills self.stations and self.data
        self.verbose = verbose
        self.kd_tree = cKDTree(data=list(self.data.keys())) # Data structure to efficiently find closest neighboring stations 

    def __str__(self) -> str:
        return "Map contains the following stations:" + "\n".join([station.__str__() for station in self.stations])
    
    def __repr__(self) -> str:
        return self.data
    
    def add_station(self, station: Station) -> None:
        assert all(-1 < coordinate < self.size for coordinate in station.location), f"Tried to add station with coordinates {station.location}, but the map's size is only {self.size}."
        assert station.location not in self.data, "Cannot add multiple stations at the same coordinates."
        self.stations = np.append(self.stations, station)
        self.data[station.location] = station.data
    
    def add_stations(self, stations: list[Station]) -> None:
        for station in stations:
            self.add_station(station)

    def location_is_occupied(self, location: tuple[int, int]) -> bool:
        return location in self.data

    def get_data(self, location: tuple[int, int]) -> tuple[float, float, float]:
        """
        Function to query data from a certain location on the map, 
        interpolating the data from the 3 closest stations.

        Parameters:
            location : (x,y)
                Point of query on the map.
        
        Returns:
            A tuple (air_quality, population_density, vegetation_cover) for the queried location.
        """

        # If there is a station exactly at the queried location
        if location in self.data:
            return self.data[location]

        if self.verbose:
            print(f"Calculating the data for {location}\nThe closest triangle of stations was:")

        n_stations = 3
        # Build reference triangle for interpolation
        while True:
            reference_triangle = np.zeros((0,2))
            # Find closest stations
            _ , indices  = self.kd_tree.query(location, n_stations)
            # We can always use the 2 closest, since stations can't be added to the same location
            lin_indep_indices = np.concatenate((indices[:2], indices[-1:]))
            closest_stations = self.stations[lin_indep_indices]
            for station in closest_stations:
                reference_triangle =  np.vstack((reference_triangle, np.array(station.location)))
            # Break condition
            if linearly_independent(triangle=reference_triangle):
                break
            # If we don't have a triangle yet, we need to find a new station
            n_stations += 1          

        # Extract data for interpolation
        triangle_data = np.empty((3,0))
        for station in closest_stations:
            if self.verbose:
                print(station)
            triangle_data = np.hstack((triangle_data, station.data.reshape(-1, 1)))

        # Interpolate between the 3 triangle vertices, using barycentric coordinates
        bar_coordinates = barycentric_coordinates(reference_triangle, location)
        data = (triangle_data @ bar_coordinates).reshape(3,)
        aq, pd, vc = data

        if self.verbose:
            print(f"The barycentric coordinates were calculated to be:\n{bar_coordinates}\nThis gave the following data:\n{aq=}\n{pd=}\n{vc=}")

        return data

if __name__ == "__main__":
    s1 = Station((2, 5), air_quality=2, population_density=3, veg_cover=1)
    s2 = Station((3, 7), air_quality=2, population_density=2, veg_cover=2)
    s3 = Station((1, 3), air_quality=1, population_density=2, veg_cover=2)
    s4 = Station((80, 90), air_quality=2, population_density=2, veg_cover=2)
    stations = np.array([s1, s2, s3, s4])
    map = Map(stations, verbose=True)
    print(map)
    map.get_data((1,1))
