import requests
import json
import os
from datetime import datetime

'''
    Here all we do is get the weather forecast for the days mentioned in the request
'''

def weather_forecast(longitude, latitude, days):
    try:
        # Ensure the days parameter is valid
        days = min(max(int(days), 1), 14)  # Clamp between 1 and 14
        
        # Direct call to Open-Meteo API instead of going through backend
        url = "https://api.open-meteo.com/v1/forecast"
        
        # Set units
        units = "fahrenheit"
        precip_unit = "inch" if units == "fahrenheit" else "mm"
        windspeed_unit = "mph" if units == "fahrenheit" else "kmh"
        
        # Parameters for the API request
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "temperature_unit": units,
            "precipitation_unit": precip_unit,
            "windspeed_unit": windspeed_unit,
            "timezone": "auto",
            "forecast_days": days,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "precipitation_probability_max",
                "weathercode",
                "sunrise",
                "sunset"
            ],
            "hourly": [
                "relative_humidity_2m"
            ]
        }
        
        print(f"Requesting forecast from Open-Meteo API directly")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Format the response to match our expected structure
        location_name = get_location_name(latitude, longitude)
        formatted_data = format_forecast_data(data, location_name, units)
        return formatted_data
        
    except Exception as e:
        import traceback
        print(f"Error in weather_forecast: {str(e)}")
        print(traceback.format_exc())
        
        # Return a minimal data structure that won't break the UI
        return {
            "location": f"Location at {latitude:.4f}, {longitude:.4f}",
            "units": {
                "temperature": "fahrenheit",
                "precipitation": "inches"
            },
            "days": [],
            "updated": "Error fetching forecast",
            "error": str(e)
        }

def get_location_name(latitude, longitude):
    """Get location name using a free reverse geocoding service"""
    try:
        # Try the Open-Meteo Geocoding API first (more detailed)
        url = f"https://geocoding-api.open-meteo.com/v1/search?latitude={latitude}&longitude={longitude}&count=1"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                result = data['results'][0]
                name = result.get('name', 'Unknown')
                admin1 = result.get('admin1', '')  # State/Province
                admin2 = result.get('admin2', '')  # County/Region
                country = result.get('country', '')
                
                # Format the location name based on available data
                if country:
                    if admin1:
                        # City, State/Province, Country (e.g., San Francisco, California, USA)
                        return f"{name}, {admin1}, {country}"
                    else:
                        # City, Country (e.g., Paris, France)
                        return f"{name}, {country}"
                elif admin1:
                    # City, State/Province (if country is missing for some reason)
                    return f"{name}, {admin1}"
                else:
                    # Just city name
                    return name
                    
        # Fallback to Nominatim if Open-Meteo doesn't return good results
        try:
            nominatim_url = f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json"
            headers = {
                'User-Agent': 'Weather Forecast App/1.0'  # Required by Nominatim API
            }
            nominatim_response = requests.get(nominatim_url, headers=headers, timeout=10)
            
            if nominatim_response.status_code == 200:
                nominatim_data = nominatim_response.json()
                if 'address' in nominatim_data:
                    address = nominatim_data['address']
                    
                    # Extract city name (try multiple fields)
                    city = (address.get('city') or address.get('town') or 
                           address.get('village') or address.get('hamlet') or 
                           address.get('municipality') or address.get('county'))
                    
                    state = address.get('state')
                    country = address.get('country')
                    
                    if city and country:
                        if state:
                            return f"{city}, {state}, {country}"
                        else:
                            return f"{city}, {country}"
                    elif city:
                        return city
                    elif 'display_name' in nominatim_data:
                        # Use display_name as a last resort
                        return nominatim_data['display_name']
        except Exception as nominatim_error:
            print(f"Nominatim fallback failed: {str(nominatim_error)}")
            # Continue to the final fallback
        
        # Final fallback to coordinates if both geocoding attempts fail
        return f"Location at {latitude:.4f}, {longitude:.4f}"
    
    except Exception as e:
        print(f"Error in get_location_name: {str(e)}")
        # If any error occurs, return a fallback location name
        return f"Location at {latitude:.4f}, {longitude:.4f}"

def format_forecast_data(api_data, location_name, units="fahrenheit"):
    """Format the Open-Meteo API data into our application's format"""
    # Format date in MM/DD/YYYY format (e.g. 4/4/2025)
    def format_date(date_str):
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%-m/%-d/%Y")
        except Exception:
            return date_str
    
    # Process daily forecast data
    daily_forecasts = []
    if 'daily' in api_data and 'time' in api_data['daily']:
        daily = api_data['daily']
        for i, date_str in enumerate(daily['time']):
            # Calculate average humidity for the day
            avg_humidity = None
            if 'hourly' in api_data and 'time' in api_data['hourly'] and 'relative_humidity_2m' in api_data['hourly']:
                # Filter hourly data for this day
                hourly_times = api_data['hourly']['time']
                hourly_humidity = api_data['hourly']['relative_humidity_2m']
                
                day_humidity = []
                for j, hourly_time in enumerate(hourly_times):
                    if hourly_time.startswith(date_str) and j < len(hourly_humidity):
                        if hourly_humidity[j] is not None:
                            day_humidity.append(hourly_humidity[j])
                
                if day_humidity:
                    avg_humidity = round(sum(day_humidity) / len(day_humidity))
            
            # Get weather description
            weather_code = daily['weathercode'][i] if 'weathercode' in daily and i < len(daily['weathercode']) else None
            weather_description = get_weather_description(weather_code)
            
            # Format data for this day
            formatted_date = format_date(date_str)
            day_data = {
                "date": formatted_date,
                "temp_high": daily['temperature_2m_max'][i] if 'temperature_2m_max' in daily and i < len(daily['temperature_2m_max']) else None,
                "temp_low": daily['temperature_2m_min'][i] if 'temperature_2m_min' in daily and i < len(daily['temperature_2m_min']) else None,
                "humidity": avg_humidity,
                "precipitation": {
                    "amount": daily['precipitation_sum'][i] if 'precipitation_sum' in daily and i < len(daily['precipitation_sum']) else 0,
                    "chance": daily['precipitation_probability_max'][i] if 'precipitation_probability_max' in daily and i < len(daily['precipitation_probability_max']) else 0
                },
                "weather": weather_description
            }
            
            daily_forecasts.append(day_data)
    
    # Return the formatted data
    return {
        "location": location_name,
        "units": {
            "temperature": units,
            "precipitation": "inches" if units == "fahrenheit" else "mm"
        },
        "days": daily_forecasts,
        "updated": datetime.now().strftime('%Y-%m-%d %H:%M')
    }

def get_weather_description(code):
    """Convert weather code to description"""
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow fall",
        73: "Moderate snow fall",
        75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    
    if code is None:
        return "Unknown"
    
    return weather_codes.get(code, "Unknown")

