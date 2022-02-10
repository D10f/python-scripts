from pathlib import Path
import os
import requests

WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"
POLUTION_URL = "http://api.openweathermap.org/data/2.5/air_pollution"
UNIT = 'metric' # standard, metric or imperial
LOCATION = "London"
LATITUDE = "-0.1257"
LONGITUDE = "51.5085"
API_KEY = "3f1ce238de0cbdd3715d43e7022170a4"

WEATHER_REQUEST_URL = f"{WEATHER_URL}?q={LOCATION}&units={UNIT}&appid={API_KEY}"
POLLUTION_REQUEST_URL = f"{POLUTION_URL}?lat={LATITUDE}&lon={LONGITUDE}&appid={API_KEY}"


def get_weather_info():
  response = requests.get(WEATHER_REQUEST_URL)
  data = response.json()

  weather = data['weather'][0]['description']
  temp = data['main']['temp']
  temp_max = data['main']['temp_max']
  temp_min = data['main']['temp_min']
  humidity = data['main']['humidity']

  return f'Weather: {weather}\nTemperature: {temp}\nMaxTemp: {temp_max}\nMinTemp: {temp_min}\nHumidity: {humidity}%\n'


def get_air_pollution():
  response = requests.get(POLLUTION_REQUEST_URL)
  data = response.json()

  # Air Quality Index
  AQI = data['list'][0]['main']['aqi']

  # Concentration of Carbon Monoxide μg/m3
  CO = data['list'][0]['components']['co']

  # Concentration of Nitrogen Monoxide μg/m3
  NO = data['list'][0]['components']['no']

  # Concentration of Nitrogen Dioxide μg/m3
  NO2 = data['list'][0]['components']['no2']

  # Concentration of Ozone μg/m3
  O3 = data['list'][0]['components']['o3']

  # Concentration of Sulphure Dioxide μg/m3
  SO2 = data['list'][0]['components']['so2']

  # Concentration of Ammonia μg/m3
  NH3 = data['list'][0]['components']['nh3']

  # Concentration of Fine Particule Matter  μg/m3
  PM2_5 = data['list'][0]['components']['pm2_5']

  # Concentration of Coarse Particule Matter μg/m3
  PM10 = data['list'][0]['components']['pm10']


  return f'AQI: {AQI}\nCO: {CO}\nNO: {NO}\nNO2: {NO2}\nO3: {O3}\nSO2: {SO2}\nNH3: {NH3}\nPM2_5: {PM2_5}\nPM10: {PM10}\n'


if __name__ == '__main__':

  home_dir = Path.home()
  conky_dir = Path.joinpath(home_dir, '.config', 'conky')
  temp_file = Path.joinpath(conky_dir, 'weather_data.txt')

  if not Path.exists(temp_file):
    with open(temp_file, 'w') as file:
      file.write(get_weather_info())
      file.write(get_air_pollution())