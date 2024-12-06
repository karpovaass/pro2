from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_KEY = 'SDXLoI07Lm3YZdTrP0bXKysrAaBxReAN'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather', methods=['POST'])
def get_weather():
    start_city = request.form['start']
    end_city = request.form['end']

    # Проверка на пустые значения
    if not start_city or not end_city:
        return "Ошибка: оба поля должны быть заполнены."

    # Получение координат для городов
    start_coords = get_coordinates(start_city)
    end_coords = get_coordinates(end_city)

    if not start_coords:
        return "Упс. Неверно введён город: {}".format(start_city)

    if not end_coords:
        return "Упс. Неверно введён город: {}".format(end_city)

    # Получение данных о погоде для начальной точки
    weather_data_start = get_weather_data(start_coords)

    if not weather_data_start:
        return "Ошибка: не удалось получить данные о погоде для города {}".format(start_city)

    # Оценка погодных условий
    result = check_bad_weather(weather_data_start['temperature'], weather_data_start['wind_speed'],
                               weather_data_start['rain_probability'])

    return render_template('result.html', result=result)

def get_coordinates(city):
    try:
        # Здесь должен быть код для получения координат города
        # Пример: если город не найден, возвращаем None
        if city.lower() == 'неизвестный':
            return None
        return {'latitude': 55.7558, 'longitude': 37.6173}  # Пример координат для Москвы
    except Exception as e:
        print(f"Ошибка при получении координат: {e}")
        return None

def get_weather_data(coords):
    try:
        location_url = f'http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey={API_KEY}&q={coords["latitude"]},{coords["longitude"]}'
        location_response = requests.get(location_url)

        if location_response.status_code != 200:
            raise Exception("Ошибка при запросе к API: {}".format(location_response.status_code))

        location_data = location_response.json()
        location_key = location_data['Key']

        weather_url = f'http://dataservice.accuweather.com/forecasts/v1/daily/1day/{location_key}?apikey={API_KEY}&metric=true'
        weather_response = requests.get(weather_url)

        if weather_response.status_code != 200:
            raise Exception("Ошибка при запросе к API: {}".format(weather_response.status_code))

        weather_data = weather_response.json()

        return {
            'temperature': weather_data['DailyForecasts'][0]['Temperature']['Maximum']['Value'],
            'wind_speed': weather_data['DailyForecasts'][0]['Day']['Wind']['Speed']['Value'],
            'rain_probability': weather_data['DailyForecasts'][0]['Day']['RainProbability']
        }
    except Exception as e:
        print(f"Ошибка при получении данных о погоде: {e}")
        return None


def check_bad_weather(temperature, wind_speed, rain_probability):
    if temperature < 0 or temperature > 35:
        return "Плохие погодные условия"
    if wind_speed > 50:
        return "Плохие погодные условия"
    if rain_probability > 70:
        return "Плохие погодные условия"
    return "Хорошие погодные условия"

if __name__ == '__main__':
    app.run(debug=True, port=5001)
