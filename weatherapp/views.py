from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Avg, Max, Min, Count
from .models import WeatherData, DailySummary, UserSettings
import requests
from django.utils import timezone

API_KEY = 'bbcad2aea44b6227e819f32c1b802b5d'

def get_lat_long(location_name):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={location_name}&appid={API_KEY}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                lat = data[0]['lat']
                lon = data[0]['lon']
                return (lat, lon)
            else:
                print(f"No results found")
        else:
            print(f"Error fetching data: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return None
    

def fetch_weather_data(city):
    coordinates = get_lat_long(city)
    if not coordinates:
        return None

    lat, lon = coordinates
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def store_weather_data(data):
    city = data['name']
    temp_kelvin = data['current']['temp']
    feels_like_kelvin = data['current']['feels_like']
    main_condition = data['current']['weather'][0]['main']
    description = data['current']['weather'][0]['description']

    temperature_celsius = temp_kelvin - 273.15
    feels_like_celsius = feels_like_kelvin - 273.15

    WeatherData.objects.create(
        city=city,
        temperature_kelvin=temp_kelvin,
        temperature_celsius=temperature_celsius,
        feels_like_kelvin=feels_like_kelvin,
        feels_like_celsius=feels_like_celsius,
        main_condition=main_condition,
        description=description
    )

def aggregate_daily_summary(city):
    today = timezone.now().date()
    weather_data = WeatherData.objects.filter(city=city, timestamp__date=today)

    if weather_data.exists():
        avg_temp = weather_data.aggregate(Avg('temperature_celsius'))['temperature_celsius__avg']
        max_temp = weather_data.aggregate(Max('temperature_celsius'))['temperature_celsius__max']
        min_temp = weather_data.aggregate(Min('temperature_celsius'))['temperature_celsius__min']
        
        dominant_condition = weather_data.values('main_condition').annotate(count=Count('id')).order_by('-count').first()['main_condition']

        DailySummary.objects.update_or_create(
            city=city,
            date=today,
            defaults={
                'avg_temperature': avg_temp,
                'max_temperature': max_temp,
                'min_temperature': min_temp,
                'dominant_condition': dominant_condition,
            }
        )

def alert_user(city):
    user_settings = UserSettings.objects.filter(city=city)
    weather_data = WeatherData.objects.filter(city=city).order_by('-timestamp').first()

    if weather_data:
        current_temp = weather_data.temperature_celsius
        for setting in user_settings:
            if setting.alert_enabled:
                if current_temp > setting.temperature_threshold:
                    # Here you would send an alert (e.g., email or console notification)
                    print(f"Alert! {setting.city}: Current temperature {current_temp} exceeds threshold of {setting.temperature_threshold}")

def update_weather(request):
    cities = ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad']

    for city in cities:
        weather_data = fetch_weather_data(city)
        weather_data['name'] = city
        if weather_data:
            store_weather_data(weather_data)
            aggregate_daily_summary(city)
            alert_user(city)

    return JsonResponse({"status": "Weather data updated successfully."})

def dashboard(request):
    summaries = DailySummary.objects.all() 
    data = [
        {
            'city': summary.city,
            'date': summary.date,
            'avg_temperature': summary.avg_temperature,
            'max_temperature': summary.max_temperature,
            'min_temperature': summary.min_temperature,
            'dominant_condition': summary.dominant_condition,
        }
        for summary in summaries
    ]
    return JsonResponse(data, safe=False)

def home(request):
    return render(request,'dashboard.html')

def settings_view(request):
    if request.method == 'POST':
        city = request.POST.get('city')
        temperature_threshold = request.POST.get('temperature_threshold')
        condition_alert = request.POST.get('condition_alert')
        alert_enabled = request.POST.get('alert_enabled') == 'on'

        UserSettings.objects.update_or_create(
            city=city,
            defaults={
                'temperature_threshold': temperature_threshold,
                'condition_alert': condition_alert,
                'alert_enabled': alert_enabled,
            }
        )
        return redirect('settings_view')  # Redirect to settings page after saving

    return render(request, 'settings.html')
