import pymc3 as pm
import numpy as np
import csv
import seaborn as sns

from matplotlib import animation

import matplotlib.pyplot as plt


def get_cities(cities_csv_file="cities.csv"):
    with open(cities_csv_file, 'rU') as cities_csv:
        city_reader = csv.reader(cities_csv, delimiter=',')
        next(city_reader)  # skip first line (column headings)

        # we'll make a dict with city names as keys and coordinates as values
        # line[0] = city name, line[1] = latitude, line[2] = longitude
        cities = {line[0]: [float(line[1]), float(line[2])] for line in city_reader}

        keys = []
        latlons = []
        for key in cities:
            keys.append(key)
            latlons.append(str(cities[key]))

        x = np.array(keys)
        y = np.array(latlons)

        return dict(x=x, y=y)

data = get_cities()

# data = np.random.normal(loc=1, size=100)

with pm.Model():
    mu = pm.Normal('mu', 1, 1)
    sigma = 1.
    returns = pm.Normal('returns', mu=mu, sd=sigma, observed=data)

    step = pm.Metropolis()
    pymc3_traces = pm.sample(15000, step)

sns.distplot(pymc3_traces[2000:]['mu'], label='PyMC3 sampler')
# sns.distplot(traces[500:], label='Hand-written sampler')
plt.legend()
plt.show()