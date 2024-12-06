import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from mapApi import Map, Station
import logging
from skfuzzy import interp_membership

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define maximum values
MAX_PD = 151
"""Maximum value for population density (exclusive)\n
Unit: µg/m³ of the pollutor pm2.5"""
MAX_AP = 71
"""Maximum value for air pollution (exclusive)\n
Unit: inhabitants/ha""" 
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
#   based on scale from https://www.geocat.ch/geonetwork/srv/eng/catalog.search#/metadata/4bfbbf20-d90e-4131-8fe2-4c454ad45c16
population_density['very_low'] = fuzz.zmf(population_density.universe, a=2, b=3)
# based on scale from https://www.geocat.ch/geonetwork/srv/eng/catalog.search#/metadata/4bfbbf20-d90e-4131-8fe2-4c454ad45c16
population_density['very_low'] = fuzz.gaussmf(population_density.universe, mean=2, sigma=1)
population_density['low'] = fuzz.gaussmf(population_density.universe, mean=5, sigma=1)
population_density['medium'] = fuzz.gaussmf(population_density.universe, mean=11, sigma=2)
population_density['high'] = fuzz.gaussmf(population_density.universe, mean=28, sigma=6)
population_density['very_high'] = fuzz.gaussmf(population_density.universe, mean=80, sigma=20)
population_density['highest'] = fuzz.smf(population_density.universe, a=100, b=120)    

# Air Pollution Membership Functions
air_pollution['good'] = fuzz.zmf(air_pollution.universe, a=10, b=15)
air_pollution['moderate'] = fuzz.gaussmf(air_pollution.universe, mean=25, sigma=7)
air_pollution['unhealthy'] = fuzz.smf(air_pollution.universe, a=35, b=50)   

# Vegetation Cover Membership Functions
veg_cover['low'] = fuzz.zmf(veg_cover.universe, a=15, b=30)
veg_cover['medium'] = fuzz.gaussmf(veg_cover.universe, mean=50, sigma=15)
veg_cover['high'] = fuzz.smf(veg_cover.universe, a=65, b=85)  

# Need for Action Membership Functions
need_for_action['low'] = fuzz.zmf(need_for_action.universe, a=20, b=40)
need_for_action['medium'] = fuzz.gaussmf(need_for_action.universe, mean=50, sigma=15)
need_for_action['high'] = fuzz.smf(need_for_action.universe, a=60, b=80)  

# Define fuzzy rules
rule1 = ctrl.Rule(
    air_pollution['unhealthy'] & (population_density['very_high'] | population_density['high'] | population_density['highest']),
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

def generate_random_stations(n_stations: int, map_size: int, max_ap: int = MAX_AP, max_pd: int = MAX_PD, max_vc: int = MAX_VC) -> np.ndarray[Station]:
    """
    Generates an array of n_stations stations, placed randomly (but all with unique locations) on the map with random data.

    Parameters:
        n_stations:
            Number of stations to generate
        map_size:
            Length of map along one axis
        max_ap:
            Maximum value for randomly drawn air pollution data. Should be less than 151.
        max_pd:
            Maximum value for randomly drawn population density data. Should be less than 151.
        max_vc:
            Maximum value for randomly drawn vegetation cover data. Should be less than 101.
    
    Returns:
        An np.array of stations
    """    
    assert max_ap <= MAX_AP, f"max_ap can not be >{MAX_AP}"
    assert max_pd <= MAX_PD, f"max_pd can not be >{MAX_PD}"
    assert max_vc <= MAX_VC, f"max_vc can not be >{MAX_VC}"

    # Random values for stations
    random_locations = generate_unique_random_locations(n_locations=n_stations, map_size=map_size)
    random_aq = np.random.randint(low=0, high=max_ap, size=n_stations)
    random_pd = np.random.randint(low=0, high=max_pd, size=n_stations)
    random_vc = np.random.randint(low=0, high=max_vc, size=n_stations)
    # Initiate random stations
    stations = [Station(random_locations[i], random_aq[i], random_pd[i], random_vc[i]) for i in range(n_stations)]
    return np.array(stations)

def generate_unique_random_locations(n_locations: int, map_size: int) -> list[tuple[int, int]]:
        """
        Generates a list of n_locations unique locations where x,y < map_size
        """
        assert n_locations <= map_size**2, f"The map is too small to have this many unique locations!\n({n_locations=}, {map_size=})"
        unique_locations = set()
        while len(unique_locations) < n_locations:
            unique_locations.add((np.random.randint(0, map_size), np.random.randint(0, map_size)))
        return list(unique_locations)

#Fuzzy labels for hover

def get_air_pollution_label(value):
    """
    Computes the fuzzy label for air pollution value.
    """
    if value < 0 or value > MAX_AP:
        return "Undefined"

    good = interp_membership(air_pollution.universe, air_pollution['good'].mf, value)
    moderate = interp_membership(air_pollution.universe, air_pollution['moderate'].mf, value)
    unhealthy = interp_membership(air_pollution.universe, air_pollution['unhealthy'].mf, value)

    degrees = {'Good': good, 'Moderate': moderate, 'Unhealthy': unhealthy}
    max_label = max(degrees, key=degrees.get)
    max_degree = degrees[max_label]

    if max_degree == 0:
        return "Undefined"

    return max_label

def get_population_density_label(value):
    """
    Computes the fuzzy label for population density value.
    """
    if value < 0 or value > MAX_PD:
        return "Undefined"

    very_low = interp_membership(population_density.universe, population_density['very_low'].mf, value)
    low = interp_membership(population_density.universe, population_density['low'].mf, value)
    medium = interp_membership(population_density.universe, population_density['medium'].mf, value)
    high = interp_membership(population_density.universe, population_density['high'].mf, value)
    very_high = interp_membership(population_density.universe, population_density['very_high'].mf, value)
    highest = interp_membership(population_density.universe, population_density['highest'].mf, value)

    degrees = {
        'Very Low': very_low,
        'Low': low,
        'Medium': medium,
        'High': high,
        'Very High': very_high,
        'Highest': highest
    }
    max_label = max(degrees, key=degrees.get)
    max_degree = degrees[max_label]

    if max_degree == 0:
        return "Undefined"

    return max_label

def get_veg_cover_label(value):
    """
    Computes the fuzzy label for vegetation cover value.
    """
    if value < 0 or value > MAX_VC:
        return "Undefined"

    low = interp_membership(veg_cover.universe, veg_cover['low'].mf, value)
    medium = interp_membership(veg_cover.universe, veg_cover['medium'].mf, value)
    high = interp_membership(veg_cover.universe, veg_cover['high'].mf, value)

    degrees = {'Low': low, 'Medium': medium, 'High': high}
    max_label = max(degrees, key=degrees.get)
    max_degree = degrees[max_label]

    if max_degree == 0:
        return "Undefined"

    return max_label

def get_need_for_action_label(value):
    """
    Computes the fuzzy label for need for action value.
    """
    if value < 0 or value > 100:
        return "Undefined"

    low = interp_membership(need_for_action.universe, need_for_action['low'].mf, value)
    medium = interp_membership(need_for_action.universe, need_for_action['medium'].mf, value)
    high = interp_membership(need_for_action.universe, need_for_action['high'].mf, value)

    degrees = {'Low': low, 'Medium': medium, 'High': high}
    max_label = max(degrees, key=degrees.get)
    max_degree = degrees[max_label]

    if max_degree == 0:
        return "Undefined"

    return max_label

    plt.show()

def get_recommendation(air_quality_label: str, population_density_label: str, veg_cover_label: str, need_for_action_label: str) -> str:
    """
    Provides a recommendation string based on the fuzzy labels for air pollution,
    population density, vegetation cover, and need for action.
    """

    # Start with need_for_action, as it's the primary driver of urgency
    if need_for_action_label == "High":
        # High need for action requires strong measures
        if veg_cover_label in ["Low", "Very Low"]:
            return ("Need for action is high and vegetation cover is low.<br> "
                    "Consider creating more green areas (planting trees, building parks)<br> "
                    "to improve air quality and reduce heat islands.<br>")
        else:
            # Veg cover is medium or high, so focus on pollution sources
            return ("Need for action is high. Vegetation cover is already moderate or high.<br> "
                    "Focus on reducing pollution sources: implement traffic calming measures,<br> "
                    "promote public transport, limit industrial emissions, or encourage cleaner technologies.<br>")
    
    elif need_for_action_label == "Medium":
        # Moderate need for action suggests incremental changes
        # Consider air pollution and population density to guide suggestions
        if air_quality_label in ["Moderate", "Unhealthy"] and population_density_label in ["High", "Very High", "Highest"]:
            return ("Need for action is medium, and conditions suggest moderate pollution in a dense area.<br> "
                    "Implement partial traffic restrictions, promote cycling and walking, or encourage telecommuting.<br> "
                    "Increase green infrastructure moderately.")
        elif veg_cover_label in ["Low", "Very Low"]:
            return ("Need for action is moderate, and vegetation cover is low.<br> "
                    "Consider adding more vegetation (green roofs, community gardens)<br> "
                    "to improve local environmental quality.")
        else:
            return ("Need for action is medium. Conditions are not severe, but consider incremental improvements:<br> "
                    "encourage cleaner transport, add some green areas, and monitor pollution sources closely.")
    
    else:  # Need for action is low
        # Conditions are relatively good
        return ("Need for action is low. Current environmental strategies seem effective.<br> "
                "Maintain your approaches, continue monitoring air quality and population density,<br> "
                "and preserve or slightly enhance green spaces as needed.")

