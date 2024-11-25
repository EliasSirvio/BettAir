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

        # Define membership functions
        # Vegetation Cover
        veg_cover['low'] = fuzz.trimf(veg_cover.universe, [0, 0, 50])
        veg_cover['high'] = fuzz.trimf(veg_cover.universe, [50, 100, 100])

        # Building Density
        build_density['low'] = fuzz.trimf(build_density.universe, [0, 0, 50])
        build_density['high'] = fuzz.trimf(build_density.universe, [50, 100, 100])

        # Air Pollution
        air_pollution_var['low'] = fuzz.trapmf(air_pollution_var.universe, [0, 0, 12, 35])
        air_pollution_var['medium'] = fuzz.trimf(air_pollution_var.universe, [12, 35, 55])
        air_pollution_var['high'] = fuzz.trapmf(air_pollution_var.universe, [35, 55, 500, 500])

        # Population Density
        population_density_var['low'] = fuzz.trimf(population_density_var.universe, [0, 0, 10000])
        population_density_var['high'] = fuzz.trimf(population_density_var.universe, [10000, 20000, 20000])

        # Risk Level
        risk_level['low'] = fuzz.trimf(risk_level.universe, [0, 0, 50])
        risk_level['medium'] = fuzz.trimf(risk_level.universe, [25, 50, 75])
        risk_level['high'] = fuzz.trimf(risk_level.universe, [50, 100, 100])

        # Define rules
        rule1 = ctrl.Rule(veg_cover['high'] & air_pollution_var['low'], risk_level['low'])
        rule2 = ctrl.Rule(veg_cover['low'] & air_pollution_var['high'], risk_level['high'])
        rule3 = ctrl.Rule(build_density['high'] & air_pollution_var['high'], risk_level['high'])
        rule4 = ctrl.Rule(population_density_var['high'] & air_pollution_var['high'], risk_level['high'])
        rule5 = ctrl.Rule(air_pollution_var['medium'], risk_level['medium'])
        rule6 = ctrl.Rule(veg_cover['low'] & build_density['high'], risk_level['high'])
        rule7 = ctrl.Rule(veg_cover['high'] & build_density['low'], risk_level['low'])
        rule8 = ctrl.Rule(air_pollution_var['low'] & population_density_var['low'], risk_level['low'])
        # You can add more rules as needed

        # Create control system and simulation
        risk_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8])
        risk_calc = ctrl.ControlSystemSimulation(risk_ctrl)

        # Pass inputs to the control system
        risk_calc.input['veg_cover'] = vegetation_cover
        risk_calc.input['build_density'] = building_density
        risk_calc.input['air_pollution'] = air_pollution
        risk_calc.input['population_density'] = population_density

        # Compute the risk level
        risk_calc.compute()

        risk_score = risk_calc.output['risk_level']

        # Categorize risk score
        if risk_score < 33:
            risk_category = 'Low'
        elif risk_score < 66:
            risk_category = 'Medium'
        else:
            risk_category = 'High'

        # Prepare explanations
        explanations = []

        # Analyze the degree of membership for each input
        veg_cover_level = 'high' if vegetation_cover > 50 else 'low'
        build_density_level = 'high' if building_density > 50 else 'low'
        air_pollution_level = 'low' if air_pollution <= 35 else 'medium' if air_pollution <= 55 else 'high'
        population_density_level = 'high' if population_density > 10000 else 'low'

        explanations.append(f"Vegetation cover is considered **{veg_cover_level}** at {vegetation_cover}%.")
        explanations.append(f"Building density is considered **{build_density_level}** at {building_density}%.")
        explanations.append(f"Air pollution level is **{air_pollution_level}** at {air_pollution} µg/m³.")
        explanations.append(f"Population density is considered **{population_density_level}** at {population_density} people per sq.km.")

        # Explain which rules were activated
        activated_rules = []

        # Check each rule's activation
        if rule1.antecedent.evaluate({'veg_cover': vegetation_cover, 'air_pollution': air_pollution}):
            activated_rules.append("Rule 1: High vegetation cover and low air pollution lead to low risk.")
        if rule2.antecedent.evaluate({'veg_cover': vegetation_cover, 'air_pollution': air_pollution}):
            activated_rules.append("Rule 2: Low vegetation cover and high air pollution lead to high risk.")
        if rule3.antecedent.evaluate({'build_density': building_density, 'air_pollution': air_pollution}):
            activated_rules.append("Rule 3: High building density and high air pollution lead to high risk.")
        if rule4.antecedent.evaluate({'population_density': population_density, 'air_pollution': air_pollution}):
            activated_rules.append("Rule 4: High population density and high air pollution lead to high risk.")
        if rule5.antecedent.evaluate({'air_pollution': air_pollution}):
            activated_rules.append("Rule 5: Medium air pollution leads to medium risk.")
        if rule6.antecedent.evaluate({'veg_cover': vegetation_cover, 'build_density': building_density}):
            activated_rules.append("Rule 6: Low vegetation cover and high building density lead to high risk.")
        if rule7.antecedent.evaluate({'veg_cover': vegetation_cover, 'build_density': building_density}):
            activated_rules.append("Rule 7: High vegetation cover and low building density lead to low risk.")
        if rule8.antecedent.evaluate({'air_pollution': air_pollution, 'population_density': population_density}):
            activated_rules.append("Rule 8: Low air pollution and low population density lead to low risk.")

        if activated_rules:
            explanations.append("The following rules were activated in the fuzzy logic system:")
            explanations.extend(activated_rules)
        else:
            explanations.append("No specific rules were activated. The risk level is based on the combination of inputs.")

        return risk_score, risk_category, explanations

    except Exception as e:
        print(f"Exception in compute_risk_level: {e}")
        raise ValueError(f"Fuzzy logic computation failed: {e}")
