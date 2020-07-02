#! /usr/local/bin/python
# -*- coding: utf-8 -*-

import tm_tools

# specify a twitter username and whether you want a heated time map or a normal time map
# an eps file will be saved with the same name as the twitter username
# the axes are automatically scaled logarithmically.

screen_name_to_get = 'BarackObama'  # twitter username, aka twitter handle

# download tweets
tweets = tm_tools.grab_tweets(screen_name_to_get)

# create plot
times, times_tot_mins, sep_array = tm_tools.analyze_tweet_times(screen_name_to_get, tweets, make_heat=True)
