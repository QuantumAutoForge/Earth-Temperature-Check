import json
import requests
import os
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

def todayto1yrs():
    tdate = date.today() - relativedelta(days=1)
    if tdate.month == 2 and tdate.day == 29:
        ldate = tdate - relativedelta(years=4)
    else:
        ldate = tdate - relativedelta(years=1)
    return [str(tdate), str(ldate)]

def store(dateval, jsonData):
    date_obj = datetime.strptime(dateval, '%Y-%m-%d')
    formatted_date = date_obj.strftime('%b%Y')
    filename = f'{formatted_date}.json'

    # Check if file exists and update existing data
    if os.path.isfile(filename):
        with open(filename, 'r') as file:
            data = json.load(file)

        if dateval in data:
            data[dateval].extend(jsonData[dateval])
        else:
            data[dateval] = jsonData[dateval]
    else:
        data = jsonData

    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

    print(f"Weather data stored in {filename}")

def fetch_weather_data(lat, lon, dateval, api_key):
    url = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat},{lon}/{dateval}/{dateval}?unitGroup=metric&include=days&key=up{api_key}&contentType=json'
    response = requests.get(url)
    print(f"Fetching data for {lat},{lon} on {dateval} - Status: {response.status_code}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"⚠️ API Error {response.status_code} for {lat},{lon} on {dateval}")
        return None

def process_locations(datelist, api_key):
    filename = 'Earthgrid432.json'
    with open(filename, 'r') as file:
        datao = json.load(file)

    for dateval in datelist:
        collected_data = {dateval: []}

        for key in datao:
            if len(datao[key]) < 2:
                continue

            lat, lon = datao[key][0], datao[key][1]
            weather_data = fetch_weather_data(lat, lon, dateval, api_key)

            if weather_data:
                collected_data[dateval].append({f'{lat},{lon}': weather_data})

        store(dateval, collected_data)
        print(f"Weather data for {dateval} stored")

if __name__ == "__main__":
    print('Collecting Weather Data...')
    datelist = todayto1yrs()
    visualcrossingapi = os.getenv('VISUALCROSSINGAPI')

    process_locations(datelist, visualcrossingapi)
    print("✅ Data collection completed!")
