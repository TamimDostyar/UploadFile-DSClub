# Creator: Tamim Dostyar

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from .models import UploadedFile, Farmer
from .forms import UploadFileForm, FarmerRegistrationForm
from .ml_processor import predict_image
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import os
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

# Simple health check endpoint for Render.com to detect
def health_check(request):
    return HttpResponse("OK", status=200)

def get_location_name(latitude, longitude):
    try:
        geolocator = Nominatim(user_agent="my_agent")
        location = geolocator.reverse((latitude, longitude))
        return location.address
    except GeocoderTimedOut:
        return f"{latitude}, {longitude}"

def register(request):
    if request.method == 'POST':
        form = FarmerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = FarmerRegistrationForm()
    return render(request, 'upload/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    # Get public history of all uploaded files with predictions
    public_history = UploadedFile.objects.filter(
        prediction__isnull=False
    ).select_related('farmer').order_by('-uploaded_at')[:10]  # Show last 10 uploads
    
    return render(request, 'upload/login.html', {'public_history': public_history})

@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        if 'update_profile' in request.POST:
            user.username = request.POST.get('username')
            user.email = request.POST.get('email')
            user.phone_number = request.POST.get('phone_number')
            user.farm_location = request.POST.get('farm_location')
            
            # We're not updating the days field from the profile form anymore
            # The days value will remain unchanged
            
            if 'profile_picture' in request.FILES:
                user.profile_picture = request.FILES['profile_picture']
            
            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
            
        elif 'change_password' in request.POST:
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if not user.check_password(old_password):
                messages.error(request, 'Current password is incorrect.')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully!')
            return redirect('profile')
    
    return render(request, 'upload/profile.html')

@login_required
def migrate_weather_data(request):
    """
    One-time function to migrate weather data from session to database
    """
    file_forecasts = request.session.get('file_forecasts', {})
    migrated_count = 0
    
    if file_forecasts:
        # Get all files for this user
        files = UploadedFile.objects.filter(farmer=request.user)
        
        for file in files:
            file_id = str(file.id)
            if file_id in file_forecasts and not file.weather_forecast:
                # Transfer from session to database
                file.weather_forecast = file_forecasts[file_id]
                file.save(update_fields=['weather_forecast'])
                migrated_count += 1
        
        if migrated_count > 0:
            print(f"Migrated {migrated_count} weather records from session to database")
    
    # Mark migration as complete in the session
    request.session['weather_migration_complete'] = True
    request.session.modified = True
    
    return migrated_count

@login_required
def home(request):
    # Check if we need to migrate weather data from session to database
    if not request.session.get('weather_migration_complete', False):
        migrate_weather_data(request)
        
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.farmer = request.user
            
            # Get location data from the form
            latitude = file.latitude
            longitude = file.longitude
            
            # Get days for forecast
            days = request.POST.get('days')
            if days and days.isdigit():
                file.forecast_days = int(days)
            else:
                file.forecast_days = 2
            
            # Save the file first without location name
            file.save()
            
            # Initialize variables
            prediction = None
            confidence = None
            forecast_data = None
            error_message = None
            
            # Process the image using our ML model
            try:
                prediction, confidence = predict_image(file.file.path)
                file.prediction = prediction
                file.confidence = confidence
                
                # Get forecast data and location name if coordinates are provided
                if latitude and longitude and file.forecast_days:
                    try:
                        from .forecast import weather_forecast, get_location_name, get_disease_spread
                        
                        # Get a proper location name first
                        file.location_name = get_location_name(latitude, longitude)
                        
                        # Get weather forecast
                        forecast_data = weather_forecast(
                            longitude, 
                            latitude, 
                            file.forecast_days
                        )
                        
                        # Calculate disease spread likelihood if we have prediction and forecast data
                        if prediction and forecast_data and 'days' in forecast_data and forecast_data['days']:
                            # Initialize disease spread data storage
                            disease_spread_data = {}
                            
                            # Day indices (0-based, so day 7 is index 6, day 14 is index 13)
                            forecast_days = [
                                {'index': 6, 'name': 'day7'},     # Day 7
                                {'index': 13, 'name': 'day14'}    # Day 14
                            ]
                            
                            # Calculate for each day if available
                            for day_info in forecast_days:
                                day_index = day_info['index']
                                day_name = day_info['name']
                                
                                if len(forecast_data['days']) > day_index:
                                    day = forecast_data['days'][day_index]
                                    avg_temp = (day.get('temp_high', 0) + day.get('temp_low', 0)) / 2
                                    humidity = day.get('humidity', 0) / 100  # Convert percentage to decimal
                                    
                                    # Get spread prediction for this day
                                    spread_prediction = get_disease_spread(prediction, humidity, avg_temp)
                                    
                                    # Store the prediction for this day
                                    disease_spread_data[day_name] = {
                                        'prediction': spread_prediction,
                                        'disease': prediction,
                                        'humidity': humidity,
                                        'temperature': avg_temp,
                                        'date': day.get('date', 'Unknown date')
                                    }
                            
                            # Add spread predictions to forecast data
                            forecast_data['disease_spread'] = disease_spread_data
                        
                        # Store the forecast data in the database
                        file.weather_forecast = forecast_data
                        
                        # Also store in session for backward compatibility
                        if not request.session.get('file_forecasts'):
                            request.session['file_forecasts'] = {}
                        
                        # Use the file ID as the key
                        request.session['file_forecasts'][str(file.id)] = forecast_data
                        request.session.modified = True
                        
                    except Exception as e:
                        import traceback
                        print(f"Error fetching weather data: {str(e)}")
                        print(traceback.format_exc())
                
                # Save the file again with prediction and location name
                file.save()
                
                messages.success(request, f'File uploaded and processed successfully! Prediction: {prediction} (Confidence: {confidence:.2%})')
            except Exception as e:
                import traceback
                error_message = f"Error processing image: {str(e)}"
                print(error_message)
                print(traceback.format_exc())
                messages.error(request, error_message)
                # Still save the file but without prediction
                file.prediction = "Processing failed"
                file.confidence = 0
                file.save()
            
            return JsonResponse({
                'status': 'success' if error_message is None else 'error',
                'message': 'File uploaded successfully!' if error_message is None else error_message,
                'redirect_url': '/',
                'processed_info': {
                    'prediction': prediction,
                    'confidence': confidence,
                    'location': file.location_name,
                    'forecast': forecast_data,
                    'processed_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'error': error_message
                }
            })
    else:
        form = UploadFileForm()
    
    # Only show files uploaded by the current user
    files = UploadedFile.objects.filter(farmer=request.user).order_by('-uploaded_at')
    
    # Add weather data to files from database or session as fallback
    file_forecasts = request.session.get('file_forecasts', {})
    
    for file in files:
        # First try to get weather data from database
        if file.weather_forecast:
            file.weather_data = file.weather_forecast
        # Fallback to session if database is empty
        elif str(file.id) in file_forecasts:
            file.weather_data = file_forecasts[str(file.id)]
            # If we found it in session but not in DB, update the DB
            file.weather_forecast = file_forecasts[str(file.id)]
            file.save(update_fields=['weather_forecast'])
        else:
            # If no weather data in database or session, set to None
            file.weather_data = None
    
    return render(request, 'upload/home.html', {'form': form, 'files': files})

@login_required
def delete_file(request, file_id):
    file = get_object_or_404(UploadedFile, id=file_id, farmer=request.user)
    if file.file:
        if os.path.exists(file.file.path):
            os.remove(file.file.path)
    file.delete()
    messages.success(request, 'File deleted successfully!')
    return redirect('home')

def logout_view(request):
    auth_logout(request)
    request.session.flush()  # Clear the session
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')
@api_view(['GET'])
def forecast(request):
    """
    Get simplified daily weather forecast with temperature, humidity, and precipitation.
    
    Query parameters:
        lat (float): Latitude
        lon (float): Longitude
        days (int, optional): Number of forecast days (default: 15, max: 16)
        units (str, optional): Temperature units ('fahrenheit' or 'celsius', default: 'fahrenheit')
    """
    # Get query parameters
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    days = request.GET.get('days', '15')
    units = request.GET.get('units', 'fahrenheit').lower()
    
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
    
    # Validate units parameter
    if units not in ['fahrenheit', 'celsius']:
        return Response(
            {"error": "Units parameter must be 'fahrenheit' or 'celsius'"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Get the location name
        location_name = get_location_name(lat, lon)
        
        # Get weather forecast data
        forecast_data = get_simplified_forecast(lat, lon, days, units)
        
        # Build the response
        response_data = {
            "location": location_name,
            "units": {
                "temperature": units,
                "precipitation": "inches" if units == "fahrenheit" else "mm"
            },
            "days": forecast_data,
            "updated": datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        
        return Response(response_data)
    
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

def get_simplified_forecast(lat, lon, days=15, units="fahrenheit"):
    """Get simplified daily weather forecast"""
    
    # Open-Meteo API URL
    url = "https://api.open-meteo.com/v1/forecast"
    
    # Set units based on temperature preference
    temp_unit = units
    precip_unit = "inch" if units == "fahrenheit" else "mm"
    windspeed_unit = "mph" if units == "fahrenheit" else "kmh"
    
    # Parameters for the API request
    params = {
        "latitude": lat,
        "longitude": lon,
        "temperature_unit": temp_unit,
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
    
    # Make API request
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    # Format date in MM/DD/YYYY format (e.g. 4/4/2025)
    def format_date(date_str):
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%-m/%-d/%Y")
        except Exception:
            return date_str
    
    # Process daily forecast data
    daily_forecasts = []
    if 'daily' in data and 'time' in data['daily']:
        daily = data['daily']
        for i, date_str in enumerate(daily['time']):
            # Calculate average humidity for the day
            avg_humidity = None
            if 'hourly' in data and 'time' in data['hourly'] and 'relative_humidity_2m' in data['hourly']:
                # Filter hourly data for this day
                hourly_times = data['hourly']['time']
                hourly_humidity = data['hourly']['relative_humidity_2m']
                
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
    
    return daily_forecasts

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
