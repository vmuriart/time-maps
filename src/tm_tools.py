#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime as dt

import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as ndi
from twython import Twython


def my_secrets():
    """Store your twitter codes."""
    d = {
        'APP_KEY': '--',
        'APP_SECRET': '--',
    }

    return d


def twitter_auth2():
    """For Twython authentication."""
    secrets = my_secrets()

    app_key = secrets['APP_KEY']
    app_secret = secrets['APP_SECRET']

    twitter = Twython(app_key, app_secret, oauth_version=2)
    twitter = Twython(app_key, access_token=twitter.obtain_access_token())
    return twitter


def get_dt(s):
    """Converts a twitter time string to a datetime object."""
    split = s.split(' ')
    s = ' '.join(split[:4]) + ' ' + split[-1]
    return dt.datetime.strptime(s, '%c')


def grab_tweets(screen_name):
    """Download a user's twitter timeline, returning a list of tweets."""
    print("downloading tweets:")
    twitter = twitter_auth2()

    max_id = None
    tweets = []
    n_packets = 17  # since packets come with 200 tweets each, this will add up to 3,200 (the maximum amount)
    for i in range(n_packets):
        print("tweet packet =", i + 1)
        user_timeline = twitter.get_user_timeline(screen_name=screen_name, count=200, max_id=max_id)

        tweets += user_timeline
        max_id = user_timeline[-1]['id'] - 1

    print("number of tweets:", len(tweets))
    return tweets


def make_heated_time_map(sep_array, n_side, width):
    """Plot heated time map. Nothing is returned."""
    print("generating heated time map ...")

    # choose points within specified range. Example plot separations greater than 5 minutes:
    # indices = (sep_array[:, 0] > 5 * 60) & (sep_array[:, 1] > 5 * 60)
    indices = range(sep_array.shape[0])  # all time separations

    x_pts = np.log(sep_array[indices, 0])
    y_pts = np.log(sep_array[indices, 1])

    min_val = np.min([np.min(x_pts), np.min(y_pts)])

    x_pts = x_pts - min_val
    y_pts = y_pts - min_val

    max_val = np.max([np.max(x_pts), np.max(y_pts)])

    x_pts *= (n_side - 1) / max_val
    y_pts *= (n_side - 1) / max_val

    img = np.zeros((n_side, n_side))

    for i in range(len(x_pts)):
        img[int(x_pts[i]), int(y_pts[i])] += 1

    img = ndi.gaussian_filter(img, width)  # apply Gaussian filter
    img = np.sqrt(img)  # taking the square root makes the lower values more visible
    img = np.transpose(img)  # needed so the orientation is the same as scatterplot

    plt.imshow(img, origin='lower')

    # create custom tick marks. Calculate positions of tick marks on the transformed log scale of the image array
    plt.minorticks_off()

    # change font, which can also now accept latex: http://matplotlib.org/users/usetex.html
    plt.rc('text', usetex=False)
    plt.rc('font', family='serif')

    my_max = np.max([np.max(sep_array[indices, 0]), np.max(sep_array[indices, 1])])
    my_min = np.max([np.min(sep_array[indices, 0]), np.min(sep_array[indices, 1])])

    pure_ticks = np.array([1e-3, 1, 10, 60 * 10, 2 * 3600, 1 * 24 * 3600, 7 * 24 * 3600])
    # where the tick marks will be placed, in units of seconds. An additional value will be appended to the end for the max
    labels = ['1 msec', '1 sec', '10 sec', '10 min', '2 hr', '1 day', '1 week']  # tick labels

    index_lower = np.min(np.nonzero(pure_ticks >= my_min))
    # index of minimum tick that is greater than or equal to the smallest time interval. This will be the first tick with a non-blank label

    index_upper = np.max(np.nonzero(pure_ticks <= my_max))
    # similar to index_lower, but for upperbound

    ticks = pure_ticks[index_lower: index_upper + 1]
    ticks = np.log(np.hstack((my_min, ticks, my_max)))  # append values to beginning and end in order to specify the limits
    ticks = ticks - min_val
    ticks *= (n_side - 1) / max_val

    labels = np.hstack(('', labels[index_lower:index_upper + 1], ''))  # append blank labels to beginning and end
    plt.xticks(ticks, labels, fontsize=16)
    plt.yticks(ticks, labels, fontsize=16)
    plt.xlabel('Time Before Tweet', fontsize=18)
    plt.ylabel('Time After Tweet', fontsize=18)
    plt.show()


def make_time_map(times_tot_mins, sep_array):
    """Plot standard, scatter-plot time map. Nothing is returned."""
    print("rendering normal time map ...")

    fig = plt.figure()
    ax = fig.add_subplot(111)

    plt.rc('text', usetex=False)
    plt.rc('font', family='serif')

    colormap = plt.cm.get_cmap('rainbow')  # see color maps at http://matplotlib.org/users/colormaps.html

    order = np.argsort(times_tot_mins[1:-1])  # so that the red dots are on top
    # order = np.arange(1, len(times_tot_mins) - 2) # dots are unsorted

    sc = ax.scatter(
        sep_array[:, 0][order], sep_array[:, 1][order],
        c=times_tot_mins[1:-1][order],
        vmin=0, vmax=24 * 60,
        s=25, cmap=colormap,
        marker='o', edgecolors='none',
    )
    # taken from http://stackoverflow.com/questions/6063876/matplotlib-colorbar-for-scatter

    color_bar = fig.colorbar(sc, ticks=[0, 24 * 15, 24 * 30, 24 * 45, 24 * 60], orientation='horizontal', shrink=0.5)
    color_bar.ax.set_xticklabels(['Midnight', '18:00', 'Noon', '6:00', 'Midnight'])
    color_bar.ax.invert_xaxis()
    color_bar.ax.tick_params(labelsize=16)

    ax.set_yscale('log')  # logarithmic axes
    ax.set_xscale('log')

    plt.minorticks_off()
    pure_ticks = np.array([1e-3, 1, 10, 60 * 10, 2 * 3600, 1 * 24 * 3600, 7 * 24 * 3600])  # where the tick marks will be placed, in units of seconds.
    labels = ['1 msec', '1 sec', '10 sec', '10 min', '2 hr', '1 day', '1 week']  # tick labels

    max_val = np.max([np.max(sep_array[:, 0]), np.max(sep_array[:, 1])])

    ticks = np.hstack((pure_ticks, max_val))

    min_val = np.min([np.min(sep_array[:, 0]), np.min(sep_array[:, 1])])

    plt.xticks(ticks, labels, fontsize=16)
    plt.yticks(ticks, labels, fontsize=16)

    plt.xlabel('Time Before Tweet', fontsize=18)
    plt.ylabel('Time After Tweet', fontsize=18)

    plt.xlim((min_val, max_val))
    plt.ylim((min_val, max_val))

    ax.set_aspect('equal')
    plt.tight_layout()

    plt.show()


def analyze_tweet_times(screen_name, tweets, make_heat):
    """Plots a heated or normal time map, and return lists of time quantities.

    input:
    screen_name: twitter handle, not including @
    tweets: list of tweets. Each tweet is a nested dictionary
    heat: Boolean; 1 for a heated time map, 0 for a normal scatterplot

    output:
    times: list of datetimes corresponding to each tweet
    times_tot_mins: list giving the time elapsed since midnight for each tweet
    sep_array: array containing xy coordinates of the time map points"""

    tweets = tweets[::-1]  # reverse order so that most recent tweets are at the end

    times = [get_dt(tweet['created_at']) for tweet in tweets]
    timezone_shift = dt.timedelta(hours=4)  # times are in GMT. Convert to eastern time.
    times = [time - timezone_shift for time in times]

    times_tot_mins = 24 * 60 - (60 * np.array([t.hour for t in times]) + np.array([t.minute for t in times]))  # 24 * 60 - number of minutes since midnight

    seps = np.array([(times[i] - times[i - 1]).total_seconds() for i in range(1, len(times))])
    seps[seps == 0] = 1  # convert zero second separations to 1-second separations

    sep_array = np.zeros((len(seps) - 1, 2))  # 1st column: x-coords, 2nd column: y-coords
    sep_array[:, 0] = seps[:-1]
    sep_array[:, 1] = seps[1:]

    if make_heat:
        n_side = 4 * 256  # number of pixels along the x and y directions
        width = 4  # the number of pixels that specifies the width of the Gaussians for the Gaussian filter
        make_heated_time_map(sep_array, n_side, width)
    else:
        make_time_map(times_tot_mins, sep_array)

    print("writing eps file...")
    print("To avoid cluttered labels, you may have to expand the plotting window by dragging, and then save the figure")
    print("to save as an eps, type: `plt.savefig('filename.eps', format='eps', bbox_inches='tight', dpi=200)`")
    print("Done!")

    plt.savefig(screen_name + '.eps', format='eps', bbox_inches='tight', dpi=200)  # save as eps

    return times, times_tot_mins, sep_array


def main(screen_name, make_heat=True):
    # specify a twitter username and whether you want a heated time map or a normal time map
    # an eps file will be saved with the same name as the twitter username
    # the axes are automatically scaled logarithmically.

    # download tweets
    tweets = grab_tweets(screen_name)

    # create plot
    times, times_tot_mins, sep_array = analyze_tweet_times(screen_name, tweets, make_heat)


if __name__ == '__main__':
    main(screen_name='BarackObama')
