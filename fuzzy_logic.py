import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Define the fuzzy variables

# Air Pollution (PM2.5 concentration in µg/m³)
air_pollution = ctrl.Antecedent(np.arange(0, 251, 1), 'air_pollution')

# Vegetation Cover (%)
veg_cover = ctrl.Antecedent(np.arange(0, 101, 1), 'veg_cover')

# Building Density (%)
build_density = ctrl.Antecedent(np.arange(0, 101, 1), 'build_density')

# Population Density (people per sq.km)
population_density = ctrl.Antecedent(np.arange(0, 20001, 1), 'population_density')

# Microclimate Risk Level
risk_level = ctrl.Consequent(np.arange(0, 101, 1), 'risk_level')

# Membership functions for air pollution (PM2.5)
air_pollution['low'] = fuzz.trapmf(air_pollution.universe, [0, 0, 15, 30])
air_pollution['moderate'] = fuzz.trapmf(air_pollution.universe, [20, 35, 55, 70])
air_pollution['high'] = fuzz.trapmf(air_pollution.universe, [60, 80, 250, 250])

# Membership functions for vegetation cover
veg_cover['low'] = fuzz.trapmf(veg_cover.universe, [0, 0, 20, 40])
veg_cover['medium'] = fuzz.trimf(veg_cover.universe, [30, 50, 70])
veg_cover['high'] = fuzz.trapmf(veg_cover.universe, [60, 80, 100, 100])

# Membership functions for building density
build_density['low'] = fuzz.trapmf(build_density.universe, [0, 0, 20, 40])
build_density['medium'] = fuzz.trimf(build_density.universe, [30, 50, 70])
build_density['high'] = fuzz.trapmf(build_density.universe, [60, 80, 100, 100])

# Membership functions for population density
population_density['low'] = fuzz.trapmf(population_density.universe, [0, 0, 2000, 5000])
population_density['medium'] = fuzz.trimf(population_density.universe, [4000, 8000, 12000])
population_density['high'] = fuzz.trapmf(population_density.universe, [10000, 14000, 20000, 20000])

# Membership functions for risk level
risk_level['low'] = fuzz.trapmf(risk_level.universe, [0, 0, 25, 50])
risk_level['medium'] = fuzz.trimf(risk_level.universe, [40, 55, 70])
risk_level['high'] = fuzz.trapmf(risk_level.universe, [60, 75, 100, 100])

# Define the rules
rule1 = ctrl.Rule(
    air_pollution['low'] & veg_cover['high'] & build_density['low'] & population_density['low'],
    risk_level['low']
)

rule2 = ctrl.Rule(
    air_pollution['high'] | (veg_cover['low'] & build_density['high']),
    risk_level['high']
)

rule3 = ctrl.Rule(
    air_pollution['moderate'] & veg_cover['medium'] & build_density['medium'],
    risk_level['medium']
)

rule4 = ctrl.Rule(
    population_density['high'] & air_pollution['high'],
    risk_level['high']
)

rule5 = ctrl.Rule(
    veg_cover['low'] & population_density['high'],
    risk_level['high']
)

rule6 = ctrl.Rule(
    veg_cover['high'] & population_density['low'],
    risk_level['low']
)

# Create the control system
risk_control_system = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6])

def compute_risk_level(veg_cover_input, build_density_input, air_pollution_input, population_density_input):
    """
    Computes the microclimate risk level based on input parameters using fuzzy logic.

    Parameters:
    - veg_cover_input (float): Vegetation cover percentage (0-100)
    - build_density_input (float): Building density percentage (0-100)
    - air_pollution_input (float): PM2.5 concentration in µg/m³ (0-250)
    - population_density_input (float): Population density per sq.km (0-20,000)

    Returns:
    - risk_score (float): Computed risk level score (0-100)
    - risk_category (str): Categorized risk level ("Low", "Medium", "High")
    """
    try:
        # Create a new simulation instance
        risk_simulation = ctrl.ControlSystemSimulation(risk_control_system)

        # Set inputs
        risk_simulation.input['veg_cover'] = veg_cover_input
        risk_simulation.input['build_density'] = build_density_input
        risk_simulation.input['air_pollution'] = air_pollution_input
        risk_simulation.input['population_density'] = population_density_input

        # Compute the fuzzy logic
        risk_simulation.compute()

        # Get output
        risk_score = risk_simulation.output['risk_level']

        # Categorize the risk level
        if risk_score <= 50:
            risk_category = "Low"
        elif 50 < risk_score <= 70:
            risk_category = "Medium"
        else:
            risk_category = "High"

        return risk_score, risk_category

    except Exception as e:
        raise ValueError(f"Fuzzy logic computation failed: {e}")
