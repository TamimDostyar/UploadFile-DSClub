# Creator: Tamim Dostyar

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import UploadedFile
from .forms import UploadFileForm
from .ml_processor import ImageProcessor
import os
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta

def home(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save()
            
            # Process the image using our ML processor
            processor = ImageProcessor()
            result = processor.process_image(file.file.path)
            
            messages.success(request, 'File uploaded successfully! Once ML processing is connected, this image will be automatically analyzed.')
            return JsonResponse({
                'status': result['status'],
                'message': result['message'],
                'redirect_url': '/',
                'processed_info': result['results']
            })
    else:
        form = UploadFileForm()
    
    files = UploadedFile.objects.all().order_by('-uploaded_at')
    return render(request, 'upload/home.html', {'form': form, 'files': files})

def delete_file(request, file_id):
    file = get_object_or_404(UploadedFile, id=file_id)
    if file.file:
        if os.path.exists(file.file.path):
            os.remove(file.file.path)
    file.delete()
    messages.success(request, 'File deleted successfully!')
    return redirect('home')

@api_view(['GET'])
def forecast(request):
    """
    Get weather forecast based on latitude and longitude using Open-Meteo API,
    which provides free 16-day forecasts without requiring an API key.
    
    Query parameters:
        lat (float): Latitude
        lon (float): Longitude
        days (int, optional): Number of forecast days (default: 15, max: 16)
    """
    # Get query parameters
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    days = request.GET.get('days', '15')
    
    # Validate parameters
    if not lat or not lon:
        return Response(
            {"error": "Latitude and longitude parameters are required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        lat = float(lat)
        lon = float(lon)
        days = int(days)
    except ValueError:
        return Response(
            {"error": "Latitude and longitude must be valid numbers, and days must be an integer"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate days parameter
    if days < 1 or days > 16:
        return Response(
            {"error": "Days parameter must be between 1 and 16"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Step 1: Get the location name using reverse geocoding
        location_name = get_location_name(lat, lon)
        
        # Step 2: Get detailed weather forecast from Open-Meteo
        forecast_data = get_open_meteo_forecast(lat, lon, days)
        
        # Process the forecast data
        processed_data = {
            "location": location_name,
            "latitude": lat,
            "longitude": lon,
            "units": "fahrenheit",
            "forecast_source": "Open-Meteo",
            "forecast": forecast_data,
            "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return Response(processed_data)
    
    except Exception as e:
        return Response(
            {"error": f"Error fetching weather data: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def get_location_name(lat, lon):
    """Get location name using a free reverse geocoding service"""
    try:
        # Use Open-Meteo Geocoding API for reverse geocoding
        url = f"https://geocoding-api.open-meteo.com/v1/search?latitude={lat}&longitude={lon}&count=1"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                result = data['results'][0]
                name = result.get('name', 'Unknown')
                admin1 = result.get('admin1', '')
                country = result.get('country', '')
                
                if admin1 and country:
                    return f"{name}, {admin1}, {country}"
                elif admin1:
                    return f"{name}, {admin1}"
                elif country:
                    return f"{name}, {country}"
                else:
                    return name
        
        # Fallback to coordinates if geocoding fails
        return f"Location at {lat:.4f}, {lon:.4f}"
    
    except Exception:
        # If any error occurs, return a fallback location name
        return f"Location at {lat:.4f}, {lon:.4f}"

def get_open_meteo_forecast(lat, lon, days=15):
    """Get weather forecast data from Open-Meteo API"""
    
    # Open-Meteo API URL
    url = "https://api.open-meteo.com/v1/forecast"
    
    # Parameters for the API request
    params = {
        "latitude": lat,
        "longitude": lon,
        "temperature_unit": "fahrenheit",
        "windspeed_unit": "mph",
        "precipitation_unit": "inch",
        "timezone": "auto",
        "forecast_days": days,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "apparent_temperature_max",
            "apparent_temperature_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "windspeed_10m_max",
            "windgusts_10m_max",
            "winddirection_10m_dominant",
            "shortwave_radiation_sum",
            "uv_index_max",
            "weathercode"
        ],
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "weathercode",
            "windspeed_10m",
            "winddirection_10m"
        ]
    }
    
    # Make the API request
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    # Process current conditions
    current_conditions = {}
    if 'current' in data:
        current = data['current']
        
        # Get weather description based on code
        weather_code = current.get('weathercode')
        weather_description = get_weather_description(weather_code)
        
        current_conditions = {
            "temperature": current.get('temperature_2m'),
            "feels_like": current.get('apparent_temperature'),
            "humidity": current.get('relative_humidity_2m'),
            "wind_speed": current.get('windspeed_10m'),
            "wind_direction": get_wind_direction(current.get('winddirection_10m')),
            "precipitation": current.get('precipitation'),
            "description": weather_description,
            "observed_time": current.get('time')
        }
    
    # Process daily forecast data
    daily_forecasts = []
    
    if 'daily' in data:
        daily = data['daily']
        time_values = daily.get('time', [])
        
        for i in range(len(time_values)):
            date_str = time_values[i]
            
            # Get weather description based on code
            weather_code = daily.get('weathercode', [])[i] if 'weathercode' in daily and i < len(daily['weathercode']) else None
            weather_description = get_weather_description(weather_code)
            
            # Calculate wind direction
            wind_dir_value = daily.get('winddirection_10m_dominant', [])[i] if 'winddirection_10m_dominant' in daily and i < len(daily['winddirection_10m_dominant']) else None
            wind_direction = get_wind_direction(wind_dir_value)
            
            # Get precipitation probability
            precip_prob = daily.get('precipitation_probability_max', [])[i] if 'precipitation_probability_max' in daily and i < len(daily['precipitation_probability_max']) else None
            
            forecast = {
                "date": date_str,
                "temp_max": daily.get('temperature_2m_max', [])[i] if 'temperature_2m_max' in daily and i < len(daily['temperature_2m_max']) else None,
                "temp_min": daily.get('temperature_2m_min', [])[i] if 'temperature_2m_min' in daily and i < len(daily['temperature_2m_min']) else None,
                "feels_like_max": daily.get('apparent_temperature_max', [])[i] if 'apparent_temperature_max' in daily and i < len(daily['apparent_temperature_max']) else None,
                "feels_like_min": daily.get('apparent_temperature_min', [])[i] if 'apparent_temperature_min' in daily and i < len(daily['apparent_temperature_min']) else None,
                "precipitation": daily.get('precipitation_sum', [])[i] if 'precipitation_sum' in daily and i < len(daily['precipitation_sum']) else None,
                "precipitation_probability": precip_prob,
                "wind_speed": daily.get('windspeed_10m_max', [])[i] if 'windspeed_10m_max' in daily and i < len(daily['windspeed_10m_max']) else None,
                "wind_gusts": daily.get('windgusts_10m_max', [])[i] if 'windgusts_10m_max' in daily and i < len(daily['windgusts_10m_max']) else None,
                "wind_direction": wind_direction,
                "description": weather_description,
                "uv_index": daily.get('uv_index_max', [])[i] if 'uv_index_max' in daily and i < len(daily['uv_index_max']) else None
            }
            
            daily_forecasts.append(forecast)
    
    # Return both current conditions and daily forecasts
    return {
        "current": current_conditions,
        "daily": daily_forecasts
    }

def get_weather_description(code):
    """Convert Open-Meteo weather code to description"""
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

def get_wind_direction(degrees):
    """Convert wind direction in degrees to cardinal direction"""
    if degrees is None:
        return "Unknown"
    
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", 
                 "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    
    index = round(degrees / 22.5) % 16
    return directions[index]