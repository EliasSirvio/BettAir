import numpy as np
from scipy.spatial import cKDTree

class Station:
    def __init__(self, location: tuple[int, int], air_quality: int, population_density: int, veg_cover: int) -> None:
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
        """
        self.size = size
        self.stations = stations
        self.data = {}
        for station in self.stations:
            assert all(-1 < coordinate < size for coordinate in station.location), f"Tried to add station with coordinates {station.location}, but the map's size is only {self.size}."
            self.data[station.location] = station.data
        self.verbose = verbose
        self.kd_tree = cKDTree(data=list(self.data.keys())) # Data structure to efficiently find closest neighboring stations 

    def __str__(self) -> str:
        return "Map contains the following stations:" + "\n".join([station.__str__() for station in self.stations])
    
    def __repr__(self) -> str:
        return self.data
    
    def add_station(self, station: Station) -> None:
        assert all(-1 < coordinate < self.size for coordinate in station.location), f"Tried to add station with coordinates {station.location}, but the map's size is only {self.size}."
        self._stations.append(station)
    
    def add_stations(self, stations: list[Station]) -> None:
        for station in stations:
            assert all(-1 < coordinate < self.size for coordinate in station.location), f"Tried to add station with coordinates {station.location}, but the map's size is only {self.size}."
            self._stations.append(station)

    def location_is_occupied(self, location: tuple[int, int]) -> bool:
        return location in self.data

    def get_data(self, location: tuple[int, int]) -> tuple[int, int, int]:
        #TODO: Fix error when three nearest stations are on a line / point.
        """
        Function to query data from a certain location on the map, 
        interpolating the data from the 3 closest stations.
        """

        # If there is a station exactly at the queried location
        if location in self.data:
            return self.data[location]

        if self.verbose:
            print("The 3 closest stations were:")

        n_stations = 3
        rank = -1
        # Build reference triangle for interpolation
        # while rank < 2:
            # print("Iteration, rank=", rank)
            # Reset triangle    
        reference_triangle = np.zeros((0,2))
        # Find closest stations
        _ , indices  = self.kd_tree.query(location, n_stations)
        closest_stations = self.stations[indices]
        for station in closest_stations:
            reference_triangle =  np.vstack((reference_triangle, np.array(station.location)))
            # new_rank = np.linalg.matrix_rank(expended_triangle)
            # if new_rank > rank:
            #     rank = new_rank
            #     reference_triangle = expended_triangle
        # Find one more station if we don't have a triangle yet
        # n_stations += 1

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
            print(f"The barycentric coordinates were calculated to be:\n{bar_coordinates}\nThe neighbor_data looked like this:\n{triangle_data}\nThis gave the following data:\n{aq=}\n{pd=}\n{vc=}")

        return data

def barycentric_coordinates(triangle: np.ndarray, point: tuple[int, int]): #TODO: Move into utils.py
        """
        Calculate the barycentric coordinates of a point with respect to a triangle.
        
        Parameters:
        triangle : array-like, shape (3, 2)
            The vertices of the triangle.
        point : array-like, shape (2,)
            The point for which to calculate the barycentric coordinates.
        
        Returns:
        array, shape (3,)
            The barycentric coordinates of the point.
        """
        triangle = np.array(triangle)
        assert triangle.shape == (3,2), f"Triangle had wrong shape! It should have shape (3,2) but had shape {triangle.shape}."

        T = np.vstack((triangle.T, np.ones((1, 3))))
        v = np.append(point, 1)
        try:
            return np.linalg.solve(T, v)
        except np.linalg.LinAlgError:
            raise ValueError("Triangle vertices are not linearly independent!")

if __name__ == "__main__":
    s1 = Station((2, 3), air_quality=2, population_density=3, veg_cover=1)
    s2 = Station((2, 0), air_quality=2, population_density=2, veg_cover=2)
    s3 = Station((1, 2), air_quality=1, population_density=2, veg_cover=2)
    stations = np.array([s1, s2, s3])
    map = Map(stations)
    print(map)
    aq, pd, vc = map.get_data((1,1))
    print(f"At location (1,1), the interpolated data is:\n{aq=}\n{pd=}\n{vc=}")
