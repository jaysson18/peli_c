import random
from Ryhma_C_peli.Beta.Story import story
from geopy import distance
from flask import Flask, render_template
from villain import villain_moves_rounds, villain_movement, generate_directional_hints, villain_location

import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    port=3306,
    database='c_peli',
    user='root',
    password='kakkapylly',
    autocommit=True


)

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)




# Global variable for climate temperature
climate_temperature = 0


# FUNCTIONS

# select 30 airports for the game
def get_airports():
    sql = """
    SELECT airport.iso_country, airport.ident, airport.name AS airport_name, airport.type, airport.latitude_deg, airport.longitude_deg, country.name AS country_name
    FROM airport
    JOIN country ON airport.iso_country = country.iso_country
    WHERE airport.continent = 'EU' 
    AND airport.type = 'large_airport'
    AND airport.iso_country != 'RU'
    ORDER BY RAND()
    LIMIT 30;
    """

    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


# get all goals

# create new game
def create_game(cur_airport, p_name, a_ports):
    sql = "INSERT INTO game (location, screen_name) VALUES (%s, %s);"
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (cur_airport, p_name))
    g_id = cursor.lastrowid

    # add goals

    return g_id


# get airport info
def get_airport_info(icao):
    sql = f'''SELECT airport.iso_country, ident, airport.name AS airport_name, type, latitude_deg, longitude_deg, country.name AS country_name
FROM airport
JOIN country ON airport.iso_country = country.iso_country
WHERE ident = %s'''
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (icao,))
    result = cursor.fetchone()
    if 'airport_name' not in result or 'country_name' not in result:
        raise KeyError("Missing keys 'airport_name' and/or 'country_name' in the database result.")

    return result


# check if airport has a goal


# calculate distance between two airports
def calculate_distance(current, target):
    start = get_airport_info(current)
    end = get_airport_info(target)
    return distance.distance((start['latitude_deg'], start['longitude_deg']),
                             (end['latitude_deg'], end['longitude_deg'])).km


# get airports in range
def airports_in_range(icao, a_ports):
    airports_with_country = []
    for airport in a_ports:
        airport_info = get_airport_info(airport['ident'])
        airports_with_country.append({
            'ident': airport['ident'],
            'name': airport['airport_name'],
            'distance': calculate_distance(icao, airport['ident']),
            'country': airport_info['country_name']
        })
    return airports_with_country


# game starts
# ask to show the story
storyDialog = input('Do you want to read the background story? (Y/N): ')
if storyDialog == 'Y' or storyDialog == "y":
    # print wrapped string line by line
    for line in story.getStory():
        print(line)

# GAME SETTINGS
print('When you are ready to start, ')
player = input('Type your player name: ')
# boolean for game over and win
game_over = False
win = False

# all airports
all_airports = get_airports()
villain_moves_rounds(all_airports)
# start_airport ident
start_airport = all_airports[0]['ident']

# current airport
current_airport = start_airport

# game id
game_id = create_game(current_airport, player, all_airports)

# GAME LOOP
while not game_over:
    # get current airport info
    airport = get_airport_info(current_airport)
    # show game status
    print(f'''You are at {airport['airport_name']}.''')
    print('You have unlimited range.')
    print(f"Climate temperature is now +{climate_temperature}C.")
    # pause
    input('\033[32mPress Enter to continue...\033[0m')

    hint = generate_directional_hints(get_airport_info(current_airport), villain_location)
    print(f"Hint: {hint}")

    # show airports in range. if none, game over
    airports = airports_in_range(current_airport, all_airports)
    airports.sort(key=lambda airport: calculate_distance(current_airport, airport['ident']))
    print(f'''\033[34mThere are {len(airports)} airports in range: \033[0m''')
    if len(airports) == 0:
        print('You are out of range.')
        game_over = True
    else:
        print(f'''Airports: ''')
        for i, airport in enumerate(airports, start=1):
            ap_distance = calculate_distance(current_airport, airport['ident'])
            print(f'''{i}. {airport['name']}, Country: {airport['country']},  distance: {ap_distance:.0f}km''')

        print(f"Climate temperature is now +{climate_temperature}")
        print(f"Hint: {hint}")
        dest = int(input('Enter the number of the airport you want to fly to: '))
        if dest >= 1 and dest <= len(airports):
            selected_distance = airports[dest - 1]
            dest = selected_distance['ident']
            selected_distance = calculate_distance(current_airport, dest)
            current_airport = dest

        # Update the climate temperature for every 100km flown
        while selected_distance >= 100:
            climate_temperature += 0.05
            selected_distance -= 100

            # Check if the climate temperature has reached a critical point
            if climate_temperature >= 6:
                print(f"Climate temperature is now +{climate_temperature:.2f}C!")
                print("The world has exploded, and you are doomed!")
                game_over = True
                break

        # check if the player's current airport matches the villain's location
        if current_airport == villain_location['ident']:
            print("You found the villain!")
            win = True
            game_over = True
        else:
            villain_movement()

        # check if the villain has reached a certain location

# show game result
print(
    f'''{f'Good job {player}! You chased down the BBC. Climate temperature rose +{climate_temperature:.2f}C, but thanks to you reclaming the climate stabilizer and turning it back on everything is back to normal. Great job!' if win else f'You lost! Better luck next time {player}. The villain location is:  {villain_location["airport_name"]} :('}''')
