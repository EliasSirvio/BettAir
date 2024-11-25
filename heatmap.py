import matplotlib.pyplot as plt
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from map import Map, Station
from tqdm import tqdm

PLOTTING = False

# Create universe variables
    # Input
population_density = ctrl.Antecedent(np.arange(0, 20001, 1), 'population_density')
air_pollution = ctrl.Antecedent(np.arange(0, 151, 1), 'air_pollution')
veg_cover = ctrl.Antecedent(np.arange(0, 101, 1), 'veg_cover')
    # Output
need_for_action = ctrl.Consequent(np.arange(0, 101, 1), 'need_for_action')
# Define membership functions for population density
population_density['very_low'] = fuzz.trapmf(population_density.universe, [0, 0, 250, 750])
population_density['low'] = fuzz.trimf(population_density.universe, [500, 1000, 1500])
population_density['medium'] = fuzz.trimf(population_density.universe, [1000, 2000, 3000])
population_density['high'] = fuzz.trimf(population_density.universe, [2500, 5000, 7500])
population_density['very_high'] = fuzz.trapmf(population_density.universe, [5000, 10000, 20000, 20000])

# Population Density Membership Functions
if PLOTTING:
    population_density.view()
    plt.title('Population Density Membership Functions')
    plt.xlabel('Population Density (people/km²)')
# Define membership functions for air pollution
air_pollution['good'] = fuzz.trapmf(air_pollution.universe, [0, 0, 10, 15])
air_pollution['moderate'] = fuzz.trapmf(air_pollution.universe, [12, 20, 30, 40])
air_pollution['unhealthy'] = fuzz.trapmf(air_pollution.universe, [35, 50, 150, 150])


# Air Pollution Membership Functions
if PLOTTING:
    air_pollution.view()
    plt.title('Air Pollution Membership Functions')
    plt.xlabel('Air pollution (µg/m³)')
# Define membership functions for vegetation cover
veg_cover['low'] = fuzz.trapmf(veg_cover.universe, [0, 0, 15, 30])
veg_cover['medium'] = fuzz.trapmf(veg_cover.universe, [25, 40, 60, 75])
veg_cover['high'] = fuzz.trapmf(veg_cover.universe, [65, 85, 100, 100])

# Vegetation Cover Membership Functions
if PLOTTING:
    veg_cover.view()
    plt.title('Vegetation Cover Membership Functions')
    plt.xlabel('Vegetation cover (%)')
# Define membership functions for need for action
need_for_action['low'] = fuzz.trapmf(need_for_action.universe, [0, 0, 20, 40])
need_for_action['medium'] = fuzz.trimf(need_for_action.universe, [35, 50, 65])
need_for_action['high'] = fuzz.trapmf(need_for_action.universe, [60, 80, 100, 100])

# Need for Action Membership Functions
if PLOTTING:
    need_for_action.view()
    plt.title('Need for Action Membership Functions')
    plt.xlabel('Need for action(%)')


# Simplified rules
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

# Define map
N_STATIONS = 100
random_locations = [(np.random.randint(0,100), np.random.randint(0,100)) for i in range(N_STATIONS)]
random_aq = [np.random.randint(0,100) for i in range(N_STATIONS)]
random_pd = [np.random.randint(0,20000) for i in range(N_STATIONS)]
random_vc = [np.random.randint(0,100) for i in range(N_STATIONS)]
stations = []
for i in range(N_STATIONS):
    stations.append(Station(random_locations[i], random_aq[i], random_pd[i], random_vc[i]))
stations = np.array(stations)
map = Map(stations, size=100)

# Run simulation, given query location
def run(query_location, sim = simulation):
    air_pollution, population_density, veg_cover = map.get_data(query_location)
    sim.input['veg_cover'] = veg_cover                      # Vegetation Cover (%)
    sim.input['air_pollution'] = air_pollution              # µg/m³
    sim.input['population_density'] = population_density    # people/km² (Very High)
    sim.compute()
    return sim.output['need_for_action']

heatmap = np.empty((map.size, map.size))
for i in tqdm(range(map.size)):
    for j in range(map.size):
        heatmap[i,j] = run((i,j))
plt.imshow(heatmap, cmap='hot', interpolation='bicubic')
plt.colorbar(label='Need for action')
plt.title('Severity Heatmap', pad=10)
plt.xlabel("West <----> East")
plt.ylabel("South <----> North")
plt.scatter([x for x,y in map.data.keys()], [y for x,y in map.data.keys()], color='g', marker='o', label="Stations")
plt.legend()
plt.show()