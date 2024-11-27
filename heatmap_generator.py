# heatmap_generator.py
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend suitable for scripts
import matplotlib.pyplot as plt
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from tqdm import tqdm
import os

# Define the heatmap generation function
def generate_heatmap():
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

    # Define membership functions for air pollution
    air_pollution['good'] = fuzz.trapmf(air_pollution.universe, [0, 0, 10, 15])
    air_pollution['moderate'] = fuzz.trapmf(air_pollution.universe, [12, 20, 30, 40])
    air_pollution['unhealthy'] = fuzz.trapmf(air_pollution.universe, [35, 50, 150, 150])

    # Define membership functions for vegetation cover
    veg_cover['low'] = fuzz.trapmf(veg_cover.universe, [0, 0, 15, 30])
    veg_cover['medium'] = fuzz.trapmf(veg_cover.universe, [25, 40, 60, 75])
    veg_cover['high'] = fuzz.trapmf(veg_cover.universe, [65, 85, 100, 100])

    # Define membership functions for need for action
    need_for_action['low'] = fuzz.trapmf(need_for_action.universe, [0, 0, 20, 40])
    need_for_action['medium'] = fuzz.trimf(need_for_action.universe, [35, 50, 65])
    need_for_action['high'] = fuzz.trapmf(need_for_action.universe, [60, 80, 100, 100])

    # Define rules
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

    # Initiate simulation
    simulation = ctrl.ControlSystemSimulation(ctrl_sys)

    # Define map size
    map_size = 100  # Adjust as needed

    # Create empty heatmap array
    heatmap = np.empty((map_size, map_size))

    # Simulate data for the map
    # For demonstration, we'll generate synthetic data
    # In a real scenario, you would fetch real data for each location

    # Generate synthetic data arrays
    # Replace these with real data if available
    air_pollution_data = np.random.uniform(5, 100, (map_size, map_size))
    population_density_data = np.random.uniform(500, 20000, (map_size, map_size))
    veg_cover_data = np.random.uniform(0, 100, (map_size, map_size))
    
    # Run simulation for each point on the map
    for i in tqdm(range(map_size), desc="Generating Heatmap"):
        for j in range(map_size):
            # Get input data for the current point
            air_p = air_pollution_data[i, j]
            pop_dens = population_density_data[i, j]
            veg_c = veg_cover_data[i, j]

            # Set simulation inputs
            simulation.input['veg_cover'] = veg_c
            simulation.input['air_pollution'] = air_p
            simulation.input['population_density'] = pop_dens

            # Compute need for action
            simulation.compute()
            heatmap[i, j] = simulation.output['need_for_action']

    # Generate the heatmap plot
    plt.figure(figsize=(8, 6))
    plt.imshow(heatmap, cmap='hot', interpolation='bicubic')
    plt.colorbar(label='Need for Action')
    plt.title('Microclimate Risk Heatmap')
    plt.xlabel("Longitude Index")
    plt.ylabel("Latitude Index")
    plt.tight_layout()

    # Save the heatmap image to the static folder
    heatmap_path = os.path.join('static', 'heatmap.png')
    plt.savefig(heatmap_path)
    plt.close()

    return heatmap_path
