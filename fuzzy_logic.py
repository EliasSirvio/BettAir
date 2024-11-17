import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def compute_risk_level(vegetation_cover, building_density, air_pollution, population_density):
    try:
        # Define fuzzy variables
        veg_cover = ctrl.Antecedent(np.arange(0, 101, 1), 'veg_cover')
        build_density = ctrl.Antecedent(np.arange(0, 101, 1), 'build_density')
        air_pollution_var = ctrl.Antecedent(np.arange(0, 501, 1), 'air_pollution')
        population_density_var = ctrl.Antecedent(np.arange(0, 20001, 1), 'population_density')
        risk_level = ctrl.Consequent(np.arange(0, 101, 1), 'risk_level')

        # Membership functions for veg_cover
        veg_cover['low'] = fuzz.trimf(veg_cover.universe, [0, 0, 50])
        veg_cover['high'] = fuzz.trimf(veg_cover.universe, [50, 100, 100])

        # Membership functions for build_density
        build_density['low'] = fuzz.trimf(build_density.universe, [0, 0, 50])
        build_density['high'] = fuzz.trimf(build_density.universe, [50, 100, 100])

        # Membership functions for air_pollution
        air_pollution_var['low'] = fuzz.trapmf(air_pollution_var.universe, [0, 0, 12, 35])
        air_pollution_var['medium'] = fuzz.trimf(air_pollution_var.universe, [12, 35, 55])
        air_pollution_var['high'] = fuzz.trapmf(air_pollution_var.universe, [35, 55, 500, 500])

        # Membership functions for population_density
        population_density_var['low'] = fuzz.trimf(population_density_var.universe, [0, 0, 10000])
        population_density_var['high'] = fuzz.trimf(population_density_var.universe, [10000, 20000, 20000])

        # Membership functions for risk_level
        risk_level['low'] = fuzz.trimf(risk_level.universe, [0, 0, 50])
        risk_level['medium'] = fuzz.trimf(risk_level.universe, [25, 50, 75])
        risk_level['high'] = fuzz.trimf(risk_level.universe, [50, 100, 100])

        # Define fuzzy rules
        rule1 = ctrl.Rule(veg_cover['low'] & air_pollution_var['high'], risk_level['high'])
        rule2 = ctrl.Rule(veg_cover['high'] & air_pollution_var['low'], risk_level['low'])
        rule3 = ctrl.Rule(build_density['high'] & air_pollution_var['high'], risk_level['high'])
        rule4 = ctrl.Rule(population_density_var['high'] & air_pollution_var['high'], risk_level['high'])
        rule5 = ctrl.Rule(air_pollution_var['medium'], risk_level['medium'])
        rule6 = ctrl.Rule(veg_cover['low'] & build_density['high'], risk_level['high'])
        rule7 = ctrl.Rule(veg_cover['high'] & build_density['low'], risk_level['low'])
        rule8 = ctrl.Rule(air_pollution_var['low'] & population_density_var['low'], risk_level['low'])
        # Add more rules as needed

        # Create control system
        risk_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8])
        risk_calc = ctrl.ControlSystemSimulation(risk_ctrl)

        # Pass inputs to the control system
        risk_calc.input['veg_cover'] = vegetation_cover
        risk_calc.input['build_density'] = building_density
        risk_calc.input['air_pollution'] = air_pollution
        risk_calc.input['population_density'] = population_density

        # Compute the risk level
        risk_calc.compute()

        # Get the risk score
        risk_score = risk_calc.output['risk_level']

        # Categorize risk score
        if risk_score < 33:
            risk_category = 'Low'
        elif risk_score < 66:
            risk_category = 'Medium'
        else:
            risk_category = 'High'

        return risk_score, risk_category

    except Exception as e:
        print(f"Exception in compute_risk_level: {e}")
        raise ValueError(f"Fuzzy logic computation failed: {e}")
