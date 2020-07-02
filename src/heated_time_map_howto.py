# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as ndi

# this code shows how to create a smoothed heatmap of a scatterplot using a Gaussian filter
# see also http://stackoverflow.com/questions/6652671/efficient-method-of-calculating-density-of-irregularly-spaced-points

# use random xy coordinates
x_coords = np.random.normal(0, 0.1, 10000)
y_coords = np.random.normal(0, 0.3, 10000)

indices = (x_coords > 0) & (x_coords < 1) & (y_coords > 0) & (y_coords < 1)  # indices of points between zero and one

x_coords = x_coords[indices]  # only use xy coords between zero and one, for simplicity
y_coords = y_coords[indices]

plt.subplot(121)  # first, a plot of the points themselves

plt.plot(x_coords, y_coords, 'b.')

plt.xlim((0, 1))
plt.ylim((0, 1))

plt.subplot(122)  # let's make a heatmap

n_side = 1024  # this is the number of bins along x and y.

H = np.zeros((n_side, n_side))  # the 'histogram' matrix that counts the number of points in each grid-square

x_heat = (n_side - 1) * x_coords  # the xy coordinates scaled to the size of the matrix
y_heat = (n_side - 1) * y_coords  # subtract 1 since Python starts counting at 0, unlike Fortran and R

for i in range(len(x_coords)):  # loop over all points to calculate the population of each bin
    H[int(x_heat[i]), int(y_heat[i])] = H[int(x_heat[i]), int(y_heat[i])] + 1  # int() outputs an integer.

    # in Python, the above line can actually be accomplished more compactly:
    # H[x_heat[i], y_heat[i]] += 1

H = ndi.gaussian_filter(H, 8)  # 8 specifies the width of the Gaussian kernel in the x and y directions
H = np.transpose(H)  # so that the orientation is the same as the scatter plot
# to bring out the individual points more, you can do: `H = np.sqrt(H)`

plt.imshow(H, origin='lower')
plt.show()
