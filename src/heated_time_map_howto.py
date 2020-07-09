# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as ndi

# For reproducibility
np.random.seed(0)

# this code shows how to create a smoothed heatmap of a scatterplot using a Gaussian filter
# see also http://stackoverflow.com/questions/6652671/efficient-method-of-calculating-density-of-irregularly-spaced-points

# use random xy coordinates
x_coords = np.random.normal(0, 0.1, 10000)
y_coords = np.random.normal(0, 0.3, 10000)

# indices of points between zero and one
indices = (x_coords > 0) & (x_coords < 1) & (y_coords > 0) & (y_coords < 1)

# only use xy coords between zero and one, for simplicity
x_coords = x_coords[indices]
y_coords = y_coords[indices]

fig, (ax0, ax1) = plt.subplots(1, 2)

# first, a plot of the points themselves
ax0.plot(x_coords, y_coords, 'b.')
ax0.set(xlim=(0, 1), ylim=(0, 1))

# let's make a heatmap
n_side = 1024  # this is the number of bins along x and y.

# the 'histogram' matrix that counts the number of points in each grid-square
img = np.zeros((n_side, n_side))

# the xy coordinates scaled to the size of the matrix
x_heat = ((n_side - 1) * x_coords).astype(int)
y_heat = ((n_side - 1) * y_coords).astype(int)

# loop over all points to calculate the population of each bin
for i in range(len(x_coords)):
    img[x_heat[i], y_heat[i]] += 1

img = ndi.gaussian_filter(img, 8)  # 8 specifies the width of the Gaussian kernel in the x and y directions
img = np.transpose(img)  # so that the orientation is the same as the scatter plot
# to bring out the individual points more, you can do: `img = np.sqrt(img)`

ax1.imshow(img, origin='lower')

fig.show()
