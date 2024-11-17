from flask import Flask, render_template, request
from fuzzy_logic import compute_risk_level
from openaq_api import get_air_quality
from recommendations import get_recommendations
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define the available location IDs and their names
locations = {
    9582: 'Bern-Bollwerk',
    3177616: 'Bern-Schwarzenburgstrasse',
    2900712: 'Bern-Kaserne',
    2162144: 'Bern-Wankdorf'
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Retrieve form data
            veg_cover_input = float(request.form['veg_cover'])
            build_density_input = float(request.form['build_density'])
            population_density_input = float(request.form['population_density'])
            location_id = int(request.form['location_id'])

            # Input validation
            errors = []
            if not (0 <= veg_cover_input <= 100):
                errors.append("Vegetation Cover must be between 0 and 100.")
            if not (0 <= build_density_input <= 100):
                errors.append("Building Density must be between 0 and 100.")
            if not (0 <= population_density_input <= 20000):
                errors.append("Population Density must be between 0 and 20,000.")
            if location_id not in locations:
                errors.append("Invalid location selected.")

            if errors:
                error_message = " ".join(errors)
                logger.warning(f"Input validation errors: {error_message}")
                return render_template('index.html', error=error_message,
                                       veg_cover=veg_cover_input,
                                       build_density=build_density_input,
                                       population_density=population_density_input,
                                       location_id=location_id,
                                       locations=locations)

            # Fetch air pollution data from selected location_id
            air_pollution_input = get_air_quality(location_id)
            if air_pollution_input is None:
                error_message = f"No air quality data available from the selected location (ID: {location_id})."
                logger.error(error_message)
                return render_template('index.html', error=error_message,
                                       veg_cover=veg_cover_input,
                                       build_density=build_density_input,
                                       population_density=population_density_input,
                                       location_id=location_id,
                                       locations=locations)

            logger.debug(f"Air pollution (PM2.5) from location {location_id}: {air_pollution_input} µg/m³")

            # Compute risk level
            risk_score, risk_category = compute_risk_level(
                veg_cover_input,
                build_density_input,
                air_pollution_input,
                population_density_input
            )

            # Get recommendations
            recommendations = get_recommendations(risk_category)

            return render_template('index.html',
                                   risk_score=risk_score,
                                   risk_category=risk_category,
                                   recommendations=recommendations,
                                   veg_cover=veg_cover_input,
                                   build_density=build_density_input,
                                   population_density=population_density_input,
                                   location_id=location_id,
                                   locations=locations)

        except ValueError as ve:
            logger.error(f"ValueError: {ve}")
            return render_template('index.html', error=str(ve), locations=locations)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return render_template('index.html', error="An unexpected error occurred. Please try again.", locations=locations)

    # For GET requests, render the page with default values
    return render_template('index.html', locations=locations)

if __name__ == '__main__':
    app.run(debug=True)
