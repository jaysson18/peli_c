# Update the climate temperature for every 100km flown
while selected_distance >= 100:
    climate_temperature += 0.05
    selected_distance -= 100

# Check if the climate temperature has reached a critical point
if climate_temperature >= 6:
    print(f"Climate temperature is now +{climate_temperature:.2f}C!")
    print("The world has exploded, and you are doomed!")
    game_over = True
