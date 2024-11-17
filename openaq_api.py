import requests

def get_air_quality(location_id):
    """
    Fetches the latest PM2.5 air quality data from the specified location_id using OpenAQ API v3.

    Parameters:
    - location_id (int): The ID of the location to fetch data from.

    Returns:
    - air_quality (float): The PM2.5 value, or None if data is unavailable.
    """
    api_key = '2caa6fe0fe5066bc5d382ec56ee1bcea909f0874444db7983cf39353caa408b2'  # Replace with your actual API key

    headers = {
        'Accept': 'application/json',
        'X-API-Key': api_key
    }

    # Step 1: Fetch sensor information to get the mapping
    url_sensors = f'https://api.openaq.org/v3/locations/{location_id}'
    try:
        response_sensors = requests.get(url_sensors, headers=headers)
        response_sensors.raise_for_status()
        data_sensors = response_sensors.json()

        if 'results' in data_sensors and data_sensors['results']:
            location_data = data_sensors['results'][0]
            sensors = location_data.get('sensors', [])
            # Create mapping from sensorsId to parameter name
            sensors_mapping = {sensor['id']: sensor['parameter']['name'] for sensor in sensors}
        else:
            print(f"No sensor data available for location_id {location_id}.")
            return None
    except Exception as e:
        print(f"Error fetching sensor data: {e}")
        return None

    # Step 2: Fetch latest measurements
    url_latest = f'https://api.openaq.org/v3/locations/{location_id}/latest'
    try:
        response_latest = requests.get(url_latest, headers=headers)
        response_latest.raise_for_status()
        data_latest = response_latest.json()

        # Print the response data for debugging
        print("API Response:")
        print(data_latest)

        if 'results' in data_latest and data_latest['results']:
            measurements = data_latest['results']
            for measurement in measurements:
                sensor_id = measurement.get('sensorsId')
                parameter_name = sensors_mapping.get(sensor_id)
                if parameter_name == 'pm25':
                    pm25_value = measurement['value']
                    return pm25_value
            print("PM2.5 data not found in the measurements.")
        else:
            print(f"No measurement data available for location_id {location_id}.")
    except Exception as e:
        print(f"Error fetching measurement data: {e}")
        return None

    return None
