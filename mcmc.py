import csv
import math
import gmplot
import os
import sys
import shutil
import timeit

from random import randint, random, shuffle
import matplotlib.pyplot as plt, numpy as np

# Traveling Salesman problem solved using MCMC (Markov Chain Monte Carlo method)
# cities is a dict of city-coordinate pairs
# MAX_ITER is the number of iterations
# T is the Markov Chain Monte Carlo temperature
# Lower temperature results in a slower mixing time, and is more likely to
# result in a local optimum, but also requires fewer iterations
def MCMC(cities, MAX_ITER=10000, T=10):
    route = list(cities.items())
    best = list(route)
    shuffle(route)

    curr_distance = total_distance(route)
    best_distance = total_distance(best)

# "route finding" for MAX_iterations, that is number of routes tested
# if new distance is shorter than curr dist then it becomes new route
# then compare this current dist to best dist and if shorter, store as best
    for _ in range(MAX_ITER):
        new_route = create_new_route(route)
        new_distance = total_distance(new_route)
        delta_distance = new_distance - curr_distance

        if (delta_distance < 0) or \
                (T > 0 and random() < math.exp(-1 * delta_distance / T)):
            route = new_route
            curr_distance = new_distance

        if curr_distance < best_distance:
            best = route
            best_distance = curr_distance

    return best


# here is where the routes are randomly generated
# 2 cities are randomly swapped to generate the new route(s)
# my dataset has 25 cities, so 2 cities are swapped with each route iteration
# route is a list of key-value tuples, e.g. ('City', [latitude, longitude])
def create_new_route(route):
    new_route = list(route)

    # generate indices for two random cities
    city_1, city_2 = (randint(0, len(route) - 1) for _ in range(2))

    # swap the cities
    new_route[city_1] = route[city_2]
    new_route[city_2] = route[city_1]

    return new_route


# route is a list of key-value tuples, e.g. ('City', [latitude, longitude])
def total_distance(route):
    dist = 0.0
    for i in range(len(route) - 1):  # skip last element
        x = route[i]
        y = route[i + 1]
        dist += distance(x, y)

    # we finish where we start, so add distances between last and first
    dist += distance(route[-1], route[0])
    return dist


# haversine distance between x and y
# in my words, this generates the 'hypotenuses' of the
# x and y are kv tuples of the form ('City', [latitude, longitude])
def distance(x, y):
    # convert degrees to radians
    lat_x, lon_x = map(math.radians, x[1])
    lat_y, lon_y = map(math.radians, y[1])

    # haversine of distance / radius
    h = (haversin(lat_y - lat_x) + math.cos(lat_x) * math.cos(lat_y)
         * haversin(lon_y - lon_x))
    r = 6371  # Radius of earth in kilometers
    d = 2.0 * r * math.asin(math.sqrt(h))
    return d


# the haversine function
def haversin(theta):
    return math.sin(theta / 2.0) ** 2


# Load the locations of the cities into memory
def get_cities(cities_csv_file="cmf_cities.csv"):
    with open(cities_csv_file, 'rU') as cities_csv:
        city_reader = csv.reader(cities_csv, delimiter=',')
        next(city_reader)  # skip first line (column headings)

        # we'll make a dict with city names as keys and coordinates as values
        # line[0] = city name, line[1] = latitude, line[2] = longitude
        cities = {line[0]: [float(line[1]), float(line[2])] for line in city_reader}
        return cities


# this is pretty straightforward. its where route distances are printed out
def print_results(route, folder_name, verbose=False):
    dist = 0.0
    for i in range(len(route) - 1):  # skip last element
        x = route[i]
        y = route[i + 1]
        tmp = distance(x, y)
        if verbose:
            print("{} and {} are {} km apart.".format(x[0], y[0], int(tmp)))
        dist += distance(x, y)

    # we finish where we start, so add distance between last and first
    x = route[-1]
    y = route[0]
    tmp = distance(x, y)
    if verbose:
        print("{} and {} are {} km apart.".format(x[0], y[0], int(tmp)))
    dist += tmp

    lats = []
    lons = []
    length = len(route)
    i = 0
    for city in route:
        if length-1 == i:
            print("{0}".format(city[0]))
        else:
            print("{0} => ".format(city[0]), end=" ")
        lats.append(city[1][0])
        lons.append(city[1][1])
        i += 1
    print("\nThe total distance is {} km.\n".format(int(dist)))

    # gmfplot to plot data on google maps and generate html page outputs
    gmap = gmplot.GoogleMapPlotter(37.428, -122.145, 6)
    gmap.plot(lats, lons, 'cornflowerblue', edge_width=10)
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)

    src = os.path.join(folder_name, "distance-{0}.html".format(int(dist)))
    gmap.draw(src)
    return dist


# this is MCMC with Simulated Annealing (i.e. T decreases over time)
# the idea here being that as T decreases the probability of accepting
# worse solutions decreases as the solution space is explored
def MCMC_SA(cities, MAX_ITER=10000, c=70):
    route = list(cities.items())
    best = list(route)
    shuffle(route)

    curr_distance = total_distance(route)
    best_distance = total_distance(best)

    for t in range(1, MAX_ITER + 1):
        T = c / math.sqrt(t)
        new_route = create_new_route(route)
        new_distance = total_distance(new_route)
        delta_distance = new_distance - curr_distance

        if (delta_distance < 0) or \
                (T > 0 and random() < math.exp(-1 * delta_distance / T)):
            route = new_route
            curr_distance = new_distance

        if curr_distance < best_distance:
            best = route
            best_distance = curr_distance

    return best

#
def run_mcmc(runs=10):
    cities = get_cities()

    print("\n====================================================\n")
    print("MCMC")
    print("\n====================================================\n")

    map_folder = "mcmc_map_results"

    min_dist = sys.maxsize
    for t in range(0, runs):
        print("Using MCMC with MAX_ITER = 10,000 and T = {0}".format(t))
        route = MCMC(cities, MAX_ITER=10000, T=t)
        dist = print_results(route,map_folder)
        if dist < min_dist:
            min_dist = dist

    print("\n")
    print("MCMC shortest distance is: {0} km".format(int(min_dist)))
    shutil.copyfile(os.path.join(map_folder, "distance-{0}.html".format(int(min_dist))),
                    "mcmc-shortest-distance-{0}.html".format(int(min_dist)))


def run_mcmc_sa(runs=10):
    cities = get_cities()

    print("\n====================================================\n")
    print("MCMC SA")
    print("\n====================================================\n")

    map_folder = "mcmc_sa_map_results"

    min_dist = sys.maxsize
    for c_value in range(0, runs):
        print("Using MCMC SA with MAX_ITER = 10,000 and c = {0}".format(c_value))
        route = MCMC_SA(cities, MAX_ITER=10000, c=c_value)
        dist = print_results(route, map_folder)
        if dist < min_dist:
            min_dist = dist

    print("\n")
    print("MCMC_SA shortest distance is: {0} km".format(int(min_dist)))
    shutil.copyfile(os.path.join(map_folder, "distance-{0}.html".format(int(min_dist))),
                    "mcmc-sa-shortest-distance-{0}.html".format(int(min_dist)))

# time how long each MCMC algorithm takes to run through its iterations
start1 = timeit.default_timer()
run_mcmc(2)
stop1 = timeit.default_timer()

start2 = timeit.default_timer()
run_mcmc_sa(2)
stop2 = timeit.default_timer()

print("\nMCMC took ", (stop1 - start1), " seconds")
print("MCMC SA took ", (stop2 - start2), " seconds")
