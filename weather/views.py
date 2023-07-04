import urllib.request
import json
from django.shortcuts import render


def index(request):

    if request.method == 'POST':
        city = request.POST['city']
        date = request.POST['date']

        source = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/forecast?q=' +
                                        city + '&units=metric&appid=2a02a1883da1ab5bf39502ff46c687c6').read()
        forecast_data = json.loads(source)

        forecasts = []
        for forecast in forecast_data['list']:
            forecast_date = forecast['dt_txt'].split()[0]  # Extract the date from the datetime
            if forecast_date == date:
                forecast_info = {
                    "datetime": forecast['dt_txt'],
                    "temp": str(forecast['main']['temp']) + ' °C',
                    "pressure": str(forecast['main']['pressure']),
                    "humidity": str(forecast['main']['humidity']),
                    'main': str(forecast['weather'][0]['main']),
                    'description': str(forecast['weather'][0]['description']),
                    'icon': forecast['weather'][0]['icon'],
                }
                forecasts.append(forecast_info)

        data = {
            "country_code": str(forecast_data['city']['country']),
            "coordinate": str(forecast_data['city']['coord']['lon']) + ', '
            + str(forecast_data['city']['coord']['lat']),
            "forecasts": forecasts,
        }

        return render(request, "weather/weather.html", data)

    return render(request, "weather/weather.html")