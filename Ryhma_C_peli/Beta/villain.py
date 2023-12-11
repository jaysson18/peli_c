import random
from geopy import distance

class Villain:
    def __init__(self):
        self.villain_location = None
        self.v_visited_airports = set()

    def villain_moves_rounds(self, player_airports):
        if not player_airports:
            print("No airports found in the database.")
            return

        # Step 2: Randomly select an initial airport for the villain
        initial_airport = random.choice(player_airports)
        self.villain_location = initial_airport
        self.v_visited_airports.add(self.villain_location['ident'])
        print(f"Villain is on the run")

    def villain_movement(self, all_airports, current_airport):
        # Calculate distances from the villain's current location to all airports
        distances = []
        for airport in all_airports:
            if airport['ident'] != self.villain_location['ident'] and airport['ident'] not in self.v_visited_airports:
                distance_value = self.calculate_distance(self.villain_location['ident'], airport['ident'])
                distances.append((airport, distance_value))

        distances.sort(key=lambda x: x[1])

        # Select the three closest unvisited airports (excluding the current one)
        closest_unvisited_airports = [airport for airport in distances if airport[0]['ident'] not in self.v_visited_airports][:3]

        if closest_unvisited_airports:
            # Choose one of the closest unvisited airports randomly
            chosen_airport = random.choice(closest_unvisited_airports)[0]

            # Update the villain's location to the chosen airport
            if chosen_airport != current_airport:
                self.villain_location = chosen_airport

                # Mark the chosen airport as visited
                self.v_visited_airports.add(self.villain_location['ident'])
        else:
            print("The villain has visited all available airports.")

    def generate_directional_hints(self, player_airport):
        lat_diff = self.villain_location['latitude_deg'] - player_airport['latitude_deg']
        lon_diff = self.villain_location['longitude_deg'] - player_airport['longitude_deg']

        if lat_diff > 0 and lon_diff > 0:
            return "The villain is to the North-East of you."
        elif lat_diff < 0 and lon_diff > 0:
            return "The villain is to the South-East of you."
        elif lat_diff > 0 and lon_diff < 0:
            return "The villain is to the North-West of you."
        elif lat_diff < 0 and lon_diff < 0:
            return "The villain is to the South-West of you."
        else:
            return "You're very close to the villain!"

    @staticmethod
    def calculate_distance(start, end):
        return distance.distance(
            (start['latitude_deg'], start['longitude_deg']),
            (end['latitude_deg'], end['longitude_deg'])
        ).km
