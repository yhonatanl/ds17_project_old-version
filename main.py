import datetime as dt
import pytz
import requests
import tzlocal
from timezonefinder import TimezoneFinder
import wikipedia
import textwrap
import json
api_key = 'f513b165eec4b1323ce1b29006f77ffe'

with open('logo.txt', 'r') as logo:
    for line in logo:
        print('\033[32m' + line, end='')


with open('settings.json', 'r') as f:
    fav_cities = json.load(f)
    city_name = fav_cities.get("1")


print(f"""\n\nThis app will provide weather information for a city of your liking. 
The current default city is {city_name}, However, you can choose another city from my favorites list,
or type a name of another city. \n""")

def choose_temperature_scale():
    # This function let the user choose between Celsius and Fahrenheit.
    global unit
    global unit_symbol
    unit_input = input(f'Would you prefer to get your weather information in Celsius or Fahrenheit?\n\n')
    if unit_input == "Celsius":
        unit = 1
        unit_symbol = 'C'
    elif unit_input == "Fahrenheit":
        unit_symbol = 'F'
    else:
        print(f"Invalid choice. the information will be in Celsius.")
        unit = int(1)
        unit_symbol = 'C'

choose_temperature_scale()

def show_system_dt():
    # This function shows the date and the system's time and location in a readable format.
    usrtz = tzlocal.get_localzone_name()
    print(f'\nToday is {now.strftime("%A")}, {now.strftime("%B")} {now.strftime("%d")}, {now.strftime("%Y")}')
    if '/' in usrtz:  # This will show the city only, instead of showing the timezone.
        print(f'The Current time is {now.strftime("%H")}:{now.strftime("%M")} in {usrtz.split("/")[-1]}\n')
    else:
        print(f'\nThe Current time is {now.strftime("%H")}:{now.strftime("%M")} in {usrtz}\n')

def get_city_info():
    # This function gets the information needed to provide the weather for the selected city.
    geocoder = requests.get(
        f'http://api.openweathermap.org/geo/1.0/direct?q={city_name}&appid={api_key}')
    latitude = geocoder.json()[0]['lat']
    longitide = geocoder.json()[0]['lon']
    tf = TimezoneFinder()
    tz_lat_lon = tf.timezone_at(lat=latitude, lng=longitide)
    pytz_timezone = pytz.timezone(tz_lat_lon)
    weatherinfo = requests.get(
        f'https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitide}&appid={api_key}&units=metric'
    )
    if unit_symbol == 'F':
        fweatherinfo = (weatherinfo.json()["main"]["temp"] * 9/5) + 33.8
        print(f'\nThe temperature in {city_name}: right now is {fweatherinfo:.2f}°{unit_symbol}, '
              f'and it feels like {fweatherinfo:.2f}°{unit_symbol}')
        print(f'\nHumidity Level: {weatherinfo.json()["main"]["humidity"]}%')
        print(f'\nCurrent time in {city_name} is {dt.datetime.now(pytz_timezone).strftime("%H:%M")}')
    else:
        print(f'\nThe temperature in {city_name}: right now is {weatherinfo.json()["main"]["temp"]}°{unit_symbol}, '
              f'and it feels like {weatherinfo.json()["main"]["feels_like"]}°{unit_symbol}')
        print(f'\nHumidity Level: {weatherinfo.json()["main"]["humidity"]}%')
        print(f'\nCurrent time in {city_name} is {dt.datetime.now(pytz_timezone).strftime("%H:%M")}')
def did_u_know(city_name):
    # This Function provide a short summary of the city's page in Wikipedia.
    try:
        entry = wikipedia.page(city_name)
        return entry.summary.split('. ')[0]
    except wikipedia.PageError:
        return f"Sorry, there is no Wikipedia page for {city_name}."
    except Exception as e:
        return f"An error occurred: {e}"
        # The exception in this function meant to deal with typical errors from wikipedia's api.

def simple_menu():
    # This function provides a simple menu. The user can either choose to show the weather information
    # for the default city, to see the list of my favorite cities, or type a name of another city.
    global city_name
    global changedefult
    changedefult = True
    print(f"Please choose an option by it's number:"
              f"\n  1. Show the weather information in {city_name}"
              f"\n  2. Show a the list of favorite cities."
              f"\n  3. Choose your own city.")
    user_choice = input("")
    if user_choice == '1':
        get_city_info()
        changedefult = False
    elif user_choice == '2':
        for rank, city in fav_cities.items():
            print(f' {rank}. {city}')
        user_city = input('\tPlease enter the name of the city: ')
        city_name = user_city
        get_city_info()
    elif user_choice == '3':
        user_city = input('Please enter the name of the city: ')
        if user_city == city_name:
            changedefult = False  # needed for if the user typed the same city as the default city.
        city_name = user_city
        get_city_info()
    else:
        print('Invalid choice. Please try again.')
        simple_menu()

now = dt.datetime.now()

show_system_dt()

simple_menu()


# city_name = input('\033[47;30mPlease Enter a city name:\033[0m \n\033[32m')

print(f'\nAbout {city_name}:\n{textwrap.fill(did_u_know(city_name),148)}.')

def update_favorite_city():
    # This function will let the user change the default city.
    if changedefult:
        update_city = input(f'\nWould you like to change the favorite city to the city you chose? (y/n) ')
        if update_city == 'y':
            with open('settings.json', 'r+') as f:
                fav_cities = json.load(f)
                fav_cities["1"] = city_name
                f.seek(0)
                json.dump(fav_cities, f, indent=4)
                f.truncate()
                print(f"\nThe favorite city is now {city_name}")
        elif update_city == 'n':
            print(f'\nThe favorite city is still {city_name}')
        else:
            print("Invalid input. Please choose 'y' or 'n' ")
            update_favorite_city()
    else:
        pass

update_favorite_city()

def re_run():
    # This will let the user run the script again.
    rerun = input(f'\nYou can try again with another city, by pressing the "enter" key. '
                  f'to exit this app - press any key + enter.\n')
    if rerun == '':
        simple_menu()
    else:
        'Thanks for trying my app!'

re_run()
