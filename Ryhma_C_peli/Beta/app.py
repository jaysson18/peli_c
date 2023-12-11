import random
from Ryhma_C_peli.Beta.Story import story
from geopy import distance
from flask import Flask, render_template
from villain import villain_moves_rounds, villain_movement, generate_directional_hints, villain_location
from game import calculate_distance

import mysql.connector


