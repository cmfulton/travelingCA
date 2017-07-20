import numpy as np
import scipy.integrate as integrate


def cub_root(x):
    return x**3

given_area = integrate.quad(cub_root, 0, 10)[0]
given_mean = given_area / 10.

print('Give area:', given_area, ' Given mean:', given_mean)

samples = cub_root(np.random.uniform(0, 10, 1000))
approx_mean = np.mean(samples)
approx_area = approx_mean * 10

print(approx_mean, given_mean)