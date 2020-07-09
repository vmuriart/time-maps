#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.ndimage as ndi
import yaml
from twython import Twython

# Custom tick marks. Where the tick marks will be placed, in units of seconds.
TICKS = (1e-3, 1, 10, 60 * 10, 2 * 3600, 1 * 24 * 3600, 7 * 24 * 3600)
LABELS = ('1 msec', '1 sec', '10 sec', '10 min', '2 hr', '1 day', '1 week')


def twitter_auth():
    """For Twitter authentication.

    Loads from file `credentials.yml` with the format:
    ```
    'APP_KEY': '---'
    'APP_SECRET': '---'
    ```
    """
    with open('credentials.yml') as f:
        secrets = yaml.load(f, Loader=yaml.BaseLoader)

    auth = Twython(secrets['APP_KEY'], secrets['APP_SECRET'], oauth_version=2)
    twitter = Twython(access_token=auth.obtain_access_token())
    return twitter


def download_tweets(screen_name):
    """Download a user's twitter timeline, returning a list of tweets."""
    print("Downloading tweets:")
    twitter = twitter_auth()

    max_id = None
    tweets = []
    n_packets = 17  # since packets come with 200 tweets each, this will add up to 3,200 (the maximum amount)
    for i in range(n_packets):
        print("  Tweet packet:", i + 1)
        user_timeline = twitter.get_user_timeline(screen_name=screen_name, count=200, max_id=max_id)

        tweets += user_timeline
        max_id = user_timeline[-1]['id'] - 1

    print("Number of tweets:", len(tweets))
    return tweets


def make_heated_time_map(sep_array, n_side, width):
    """Plot heated time map. Nothing is returned.

    n_side: number of pixels along the x and y directions
    width: number of pixels that specifies the width of the Gaussian for the Gaussian filter
    """
    print("Generating heated time map...")
    array = np.log(sep_array)

    min_val = array.min()
    max_val = array.max() - min_val

    array = (array - min_val) * (n_side - 1) / max_val
    array = array.astype(int)

    img = np.zeros((n_side, n_side))
    for i in range(len(array)):
        img[tuple(array[i])] += 1

    img = ndi.gaussian_filter(img, width)  # apply Gaussian filter
    img = np.sqrt(img)  # taking the square root makes the lower values more visible
    img = np.transpose(img)  # needed so the orientation is the same as scatterplot

    fig, ax = plt.subplots()
    ax.imshow(img, origin='lower')

    #  Calculate positions of tick marks on the transformed log scale of the image array
    ticks = (np.log(TICKS) - min_val) * (n_side - 1) / max_val

    ax.set(
        xlim=(0, n_side), xticks=ticks, xticklabels=LABELS, xlabel='Time Before Tweet',
        ylim=(0, n_side), yticks=ticks, yticklabels=LABELS, ylabel='Time After Tweet',
    )
    ax.minorticks_off()


def make_time_map(sep_array, times_tot_mins):
    """Plot standard, scatter-plot time map. Nothing is returned."""
    print("Rendering normal time map...")

    times_tot_mins = times_tot_mins[1:-1]
    order = np.argsort(times_tot_mins)[::-1]  # so that the Morning dots are on top
    # order = np.arange(1, len(times_tot_mins)) # dots are unsorted

    # Reorder arrays
    times_tot_mins = times_tot_mins[order]
    sep_array = sep_array[order]

    fig, ax = plt.subplots(subplot_kw=dict(aspect='equal', xscale='log', yscale='log'))
    sc = ax.scatter(
        sep_array[:, 0], sep_array[:, 1],
        c=times_tot_mins,
        vmin=0, vmax=24 * 60, s=25,
        cmap=plt.cm.get_cmap('rainbow'),
        marker='o', edgecolors='none',
    )  # https://stackoverflow.com/a/6065493/5208670

    color_bar = fig.colorbar(sc, ticks=[0, 24 * 15, 24 * 30, 24 * 45, 24 * 60], orientation='horizontal', shrink=0.5)
    color_bar.ax.set_xticklabels(['Midnight', '6:00', 'Noon', '18:00', 'Midnight'])

    max_val = sep_array.max()
    min_val = sep_array.min()

    ax.set(
        xlim=(min_val, max_val), xticks=TICKS, xticklabels=LABELS, xlabel='Time Before Tweet',
        ylim=(min_val, max_val), yticks=TICKS, yticklabels=LABELS, ylabel='Time After Tweet',
    )
    ax.minorticks_off()


def analyze_tweet_times(tweets):
    """Plots a heated or normal time map, and return lists of time quantities.

    input:
    screen_name: twitter handle, not including @
    tweets: list of tweets. Each tweet is a nested dictionary
    heat: Boolean; 1 for a heated time map, 0 for a normal scatterplot

    output:
    times: list of datetimes corresponding to each tweet
    times_tot_mins: list giving the time elapsed since midnight for each tweet
    sep_array: array containing xy coordinates of the time map points"""

    # reverse order so that most recent tweets are at the end
    times = [tweet['created_at'] for tweet in reversed(tweets)]
    times = pd.to_datetime(times) - pd.Timedelta(hours=4)  # times are in GMT. Convert to eastern time.
    times = times.to_series().reset_index(drop=True)  # convert to Series

    times_tot_mins = (60 * times.dt.hour + times.dt.minute).values

    # 1st column: x-coords, 2nd column: y-coords
    seps = (times - times.shift(1)).dt.total_seconds()
    sep_array = pd.concat([seps, seps.shift(-1)], axis=1).dropna().values
    sep_array[sep_array == 0] = 1  # convert zero second separations to 1-second separations

    return times, times_tot_mins, sep_array


def main(screen_name, make_heat=True):
    """Specify a twitter username and whether you want a heated time map or a normal time map."""
    tweets = download_tweets(screen_name)

    # Prepare data
    times, times_tot_mins, sep_array = analyze_tweet_times(tweets)

    # Create plot
    if make_heat:
        make_heated_time_map(sep_array, n_side=4 * 256, width=4)
    else:
        make_time_map(sep_array, times_tot_mins)

    plt.show()


if __name__ == '__main__':
    main(screen_name='BarackObama', make_heat=True)
