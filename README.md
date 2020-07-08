# Time-Maps

This repository contains two python files for creating time maps and downloading tweets. The python files require a few packages. See below for details. To download tweets, you will need to set up your own Twitter account and paste the credentials into `credentials.yml` see `tm_tools.py` for details.

Post cool time maps to Twitter!  `#time_map_viz`

Here is a description of each file:

- `heated_time_map_howto.py` - this creates a heated time map using randomly generated points. It only requires `numpy` and `scipy` to run. 

- `tm_tools.py` - contains the functions required to actually build the time map and grab the tweets. It requires the following packages: `numpy`, `scipy`, `matplotlib`, `twython` and `pandas`. You will also need to create your twitter credentials. File downloads tweets and creates a corresponding time map. you specify the user account whose tweets you wish to download, and whether you want a heated time map or a normal time map (scatterplot).

For a quick read on time maps, check out 
[District Data Labs](https://districtdatalabs.silvrback.com/time-maps-visualizing-discrete-events-across-many-timescales).

I also wrote a longer [article](http://ieeexplore.ieee.org/xpl/articleDetails.jsp?arnumber=7363824) with more in-depth examples and connections to probability.
