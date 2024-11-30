# fuzzy_utils.py

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from map import Map, Station
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define maximum values
MAX_PD = 151
"""Maximum value for population density (exclusive)
Unit: inhabitants/ha"""
MAX_AP = 171
"""Maximum value for air pollution (exclusive)
Unit: µg/m³ of the pollutor pm2.5""" 
MAX_VC = 101
"""Maximum value for vegetation cover (exclusive)
Unit: %""" 

# Create universe variables
# Input
population_density = ctrl.Antecedent(np.arange(0, MAX_PD, 1), 'population_density')
air_pollution = ctrl.Antecedent(np.arange(0, MAX_AP, 1), 'air_pollution')
veg_cover = ctrl.Antecedent(np.arange(0, MAX_VC, 1), 'veg_cover')
# Output
need_for_action = ctrl.Consequent(np.arange(0, 101, 1), 'need_for_action')

# Define membership functions
# Population Density Membership Functions
population_density['very_low'] = fuzz.gaussmf(population_density.universe, mean=2, sigma=1)
population_density['low'] = fuzz.gaussmf(population_density.universe, mean=5, sigma=1)
population_density['medium'] = fuzz.gaussmf(population_density.universe, mean=11, sigma=4)
population_density['high'] = fuzz.gaussmf(population_density.universe, mean=28, sigma=12)
population_density['very_high'] = fuzz.gaussmf(population_density.universe, mean=80, sigma=40)
population_density['highest'] = fuzz.smf(population_density.universe, a=100, b=120)    

# Air Pollution Membership Functions
air_pollution['good'] = fuzz.trapmf(air_pollution.universe, [0, 0, 10, 15])
air_pollution['moderate'] = fuzz.trapmf(air_pollution.universe, [12, 20, 30, 40])
air_pollution['unhealthy'] = fuzz.trapmf(air_pollution.universe, [35, 50, 150, 150])   

# Vegetation Cover Membership Functions
veg_cover['low'] = fuzz.trapmf(veg_cover.universe, [0, 0, 15, 30])
veg_cover['medium'] = fuzz.trapmf(veg_cover.universe, [25, 40, 60, 75])
veg_cover['high'] = fuzz.trapmf(veg_cover.universe, [65, 85, 100, 100])  

# Need for Action Membership Functions
need_for_action['low'] = fuzz.trapmf(need_for_action.universe, [0, 0, 20, 40])
need_for_action['medium'] = fuzz.trimf(need_for_action.universe, [35, 50, 65])
need_for_action['high'] = fuzz.trapmf(need_for_action.universe, [60, 80, 100, 100])    

# Define fuzzy rules
rule1 = ctrl.Rule(
    air_pollution['unhealthy'] & (population_density['very_high'] | population_density['high']),
    need_for_action['high']
)

rule2 = ctrl.Rule(
    air_pollution['unhealthy'] & population_density['very_low'],
    need_for_action['low']
)

rule3 = ctrl.Rule(
    air_pollution['unhealthy'] & (population_density['low'] | population_density['medium']),
    need_for_action['medium']
)

rule4 = ctrl.Rule(
    air_pollution['good'],
    need_for_action['low']
)

rule5 = ctrl.Rule(
    veg_cover['high'],
    need_for_action['low']
)

rule6 = ctrl.Rule(
    air_pollution['moderate'],
    need_for_action['medium']
)

# Create control system
ctrl_sys = ctrl.ControlSystem([
    rule1, rule2, rule3, rule4, rule5, rule6 
])

def run_simulation(query_location: tuple[float, float], map_obj: Map) -> float:
    """
    Run simulation, given query location on the given map.
    
    Parameters:
    - query_location (tuple[float, float]): The (x, y) location on the map grid (float-based).
    - map_obj (Map): The map object containing stations and data.
    
    Returns:
    - float: Simulated 'need_for_action' value.
    """
    # Retrieve interpolated data
    air_pollution_val, population_density_val, veg_cover_val = map_obj.get_data(location=query_location)
    
    # Handle cases where data is unavailable
    if air_pollution_val == -1 and population_density_val == -1 and veg_cover_val == -1:
        logging.warning(f"Data unavailable for location {query_location}. Assigning 'need_for_action' = 0.")
        return 0.0  # Default value when data is unavailable
    
    try:
        # Instantiate a new simulation object for each run
        sim = ctrl.ControlSystemSimulation(ctrl_sys)
        
        # Input the data into the simulation
        sim.input['veg_cover'] = veg_cover_val                      # Vegetation Cover (%)
        sim.input['air_pollution'] = air_pollution_val              # µg/m³
        sim.input['population_density'] = population_density_val    # inhabitants/ha
        
        # Compute the simulation
        sim.compute()
        
        # Safely retrieve 'need_for_action' with a default value
        need_action = sim.output.get('need_for_action', 0.0)
        
        # Log if 'need_for_action' is not set
        if 'need_for_action' not in sim.output:
            logging.warning(f"'need_for_action' not found in simulation output for location {query_location}. Assigning 0.")
        
        return need_action
    
    except Exception as e:
        logging.error(f"Error during simulation at location {query_location}: {e}")
        return 0.0  # Assign a default or error value

def generate_random_stations(n_stations: int, map_size: int) -> np.ndarray:
    """
    Generates an array of stations, placed randomly on the map with random data.
    
    Parameters:
    - n_stations (int): Number of stations to generate.
    - map_size (int): Size of the map (assumes a square grid).
    
    Returns:
    - np.ndarray: Array of Station objects.
    """
    stations = []
    for _ in range(n_stations):
        # Generate a random location_id (ensure these are valid if using real data)
        location_id = np.random.randint(1000, 9999)  # Mock location IDs
        population_density = np.random.randint(1, MAX_PD)  # Random population density
        veg_cover = np.random.randint(1, MAX_VC)            # Random vegetation cover
        
        try:
            # Initialize the Station object with correct number of arguments
            station = Station(location_id, population_density, veg_cover)
            stations.append(station)
        except Exception as e:
            logging.error(f"Error creating Station with ID {location_id}: {e}")
            # Optionally, skip this station or assign default values
    
    return np.array(stations)
