import numpy as np
import matplotlib.pyplot as plt
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from map import Map, Station

MAX_PD = 151
"""Maximum value for population density (exclusive)\n
Unit: µg/m³ of the pollutor pm2.5"""
MAX_AP = 171
"""Maximum value for air pollution (exclusive)\n
Unit: inhabitants/ha""" 
MAX_VC = 101
"""Maximum value for vegetation cover (exclusive)\n
Unit: %""" 

# Create universe variables
    # Input
population_density = ctrl.Antecedent(np.arange(0, MAX_PD, 1), 'population_density')
air_pollution = ctrl.Antecedent(np.arange(0, MAX_AP, 1), 'air_pollution')
veg_cover = ctrl.Antecedent(np.arange(0, MAX_VC, 1), 'veg_cover')
    # Output
need_for_action = ctrl.Consequent(np.arange(0, 101, 1), 'need_for_action')

# Population Density Membership Functions
#   based on scale from https://www.geocat.ch/geonetwork/srv/eng/catalog.search#/metadata/4bfbbf20-d90e-4131-8fe2-4c454ad45c16
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


# Fuzzy rules
rule1 = ctrl.Rule(
    air_pollution['unhealthy'] & (population_density['very_high'] | population_density['high']),
    need_for_action['high']
)

rule2 = ctrl.Rule(
    air_pollution['unhealthy'] &population_density['very_low'],
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

# Initiate simulation
simulation = ctrl.ControlSystemSimulation(ctrl_sys)

def run_simulation(query_location: tuple[int, int], map: Map, sim = simulation):
    """
    Run simulation, given query location on the given map
    """
    air_pollution, population_density, veg_cover = map.get_data(query_location)
    sim.input['veg_cover'] = veg_cover                      # Vegetation Cover (%)
    sim.input['air_pollution'] = air_pollution              # µg/m³
    sim.input['population_density'] = population_density    # people/km² (Very High)
    sim.compute()
    return sim.output['need_for_action']

def generate_random_stations(n_stations: int, map_size: int) -> np.ndarray[Station]:
    """
    Generates an array of stations, placed randomly on the map with random data.
    """
    # Random values for stations
    random_locations = [(np.random.randint(0,map_size), np.random.randint(0,map_size)) for _ in range(n_stations)]
    random_aq = [np.random.randint(0,MAX_AP) for _ in range(n_stations)]
    random_pd = [np.random.randint(0,MAX_PD) for _ in range(n_stations)]
    random_vc = [np.random.randint(0,MAX_VC) for _ in range(n_stations)]
    # Initiate random stations
    stations = []
    for i in range(n_stations):
        stations.append(Station(random_locations[i], random_aq[i], random_pd[i], random_vc[i]))
    return np.array(stations)

if __name__ == "__main__":

    air_pollution.view()
    plt.title('Air Pollution Membership Functions')
    plt.xlabel('pm2.5 (µg/m³)')
    population_density.view()
    plt.title('Population Density Membership Functions')
    plt.xlabel('Population Density (inhabitants/ha)')
    veg_cover.view()
    plt.title('Vegetation Cover Membership Functions')
    plt.xlabel('Vegetation cover (%)')
    need_for_action.view()
    plt.title('Need for Action Membership Functions')
    plt.xlabel('Need for action(%)')