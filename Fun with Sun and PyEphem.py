#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Import libraries
import ephem
import math
import datetime
import geopy
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib
from matplotlib.ticker import FuncFormatter
import numpy as np


# In[2]:


# Get retina display quality for plots
get_ipython().run_line_magic('config', "InlineBackend.figure_format = 'retina'")


# In[3]:


# Set up observer
home = ephem.Observer()


# In[66]:


# Change date to desired date
home.date = '2019-01-01'


# In[67]:


# Change city name to get location coordinates or insert them manualy, in degrees
city = 'Sao Paulo'

gn = geopy.geocoders.GeoNames(username="mrbits")

location = gn.geocode("Sao Paulo")

# To set location manualy, comment the two lines bellow and uncomment the other two.
# Set latitude and logitude in degrees
home.lat = str(location.latitude)
home.lon = str(location.longitude)

# home.lat = -23.6
# home.lon = -46-6


# In[68]:


# Setup the Sun
sun = ephem.Sun()
sun.compute(home)


# In[69]:


# Compute Rising, Transit (solar noon) and set
rising = home.previous_rising(sun).datetime()
print('Sunrise is at {:02}:{:02}:{:02}'.format(rising.hour, rising.minute, rising.second))

transit = home.next_transit(sun).datetime()
print('Local noon is at {:02}:{:02}:{:02}'.format(transit.hour, transit.minute, transit.second))

setting = home.next_setting(sun).datetime()
print('Sunset is at {:02}:{:02}:{:02}'.format(setting.hour, setting.minute, setting.second))


# In[37]:


# Aparent Solar Time
matplotlib.style.use('ggplot')

# Prepare
times = []

def get_diff(tm):
    """Return a difference in seconds between tm and 12:00:00 on tm's date"""
    a = datetime.datetime.combine(tm, datetime.time(12, 0))
    return (a-tm).total_seconds()/60

# Prepare the data
for i in range(1, 368):
    home.date += ephem.Date(1)
    trans = home.next_transit(sun).datetime()
    times.append(get_diff(trans))

# Set up
ts = pd.Series(times, index=pd.date_range("2019-01-01", periods=len(times)))

# Plot graph
ax = ts.plot()
plt.rcParams["figure.figsize"] = [9, 6]
ax.set_xlabel(u'Date', fontsize=11)
ax.set_ylabel(u'Variation (minutes)', fontsize=11)
# Fire
plt.show()


# In[71]:


# Drawing Analemma
home.date = '2019/01/01 12:00:00'
home.horizon = 0
sun = ephem.Sun()
posx = []
posy = []

# Solstice altitude
phi = 90 - math.degrees(home.lat)
# Earth axial tilt
epsilon = 23.439

def get_sun_az(tm):
    """Get the azimuth based on a date"""
    sun.compute(tm)
    return math.degrees(sun.az)

def get_sun_alt(tm):
    """Get the altitude based on a date"""
    sun.compute(tm)
    return math.degrees(sun.alt)

# Prepare the data
for i in range(1, 368):
    home.date += ephem.Date(1)
    trans = home.next_transit(sun).datetime()
    posx.append(get_sun_az(home))
    posy.append(get_sun_alt(home))

# Set up
fig, ax = plt.subplots()
ax.plot(posx, posy)
ax.grid(True)
ax.set_xlabel(u'Azimuth (°)', fontsize=11)
ax.set_ylabel(u'Altitude (°)', fontsize=11)
plt.rcParams["figure.figsize"] = [9, 6]

plot_margin = 4
x0, x1, y0, y1 = plt.axis()
plt.axis((x0, x1, y0 - plot_margin, y1 + plot_margin))

# Fire
plt.show()


# In[73]:


# Twilights
# Computed by default in Ephem using Sun Edge, not center
# Difference between Edge and Center can be calculated as
initial_set = home.next_setting(sun).datetime() # zero edge
next_set = home.next_setting(sun, use_center=True).datetime() # zero centre

print('Centre sunset is at {}:{}:{}'.format(next_set.hour, next_set.minute, next_set.second))
print('Edge sunset is at {}:{}:{}'.format(initial_set.hour, initial_set.minute, initial_set.second))

delta = initial_set - next_set
print('Time difference is {} mins, {} secs'.format(delta.seconds/60, delta.seconds%60))


def get_setting_twilights(obs, body):
    """Returns a list of twilight datetimes in epoch format"""
    results = []
    # Twilights, their horizons and whether to use the centre of the Sun or not
    twilights = [('0', False), ('-6', True), ('-12', True), ('-18', True)]
    for twi in twilights:
        # Zero the horizon
        obs.horizon = twi[0]
        try:
            # Get the setting time and date
            now = obs.next_setting(body, use_center=twi[1]).datetime()
            # Get seconds elapsed since midnight
            results.append(
                (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
            )
        except ephem.AlwaysUpError:
            # There will be occasions where the sun stays up, make that max seconds
            results.append(86400.0)
    return results

home.horizon = '0'
twilights = get_setting_twilights(home, sun)
twilights


# In[74]:


# Preparing data
twidataset = []

# Calculate just over a year of data
for i in range(1, 368):
    home.date += ephem.Date(1)
    twidataset.append(get_setting_twilights(home, sun))


# In[75]:


# Plot list as a Pandas Dataframe
df = pd.DataFrame(twidataset, columns=['Sunset', 'Civil', 'Nautical', 'Astronomical'])

df[150:160]

# Data is ready


# In[77]:


# Plot Graph
def timeformatter(x, pos):
    """The two args are the value and tick position"""
    return '{}:{}:{:02d}'.format(int(x/3600), int(x/24/60), int(x%60))

def dateformatter(x, pos):
    """The two args are the value and tick position"""
    dto = datetime.date.fromordinal(datetime.date(2019, 1, 1).toordinal() + int(x) - 1)
    return '{}-{:02d}'.format(dto.year, dto.month)

plt.rcParams["figure.figsize"] = [9, 6]
ax = df.plot.area(stacked=False, color=['#e60000', '#80ccff', '#33adff', '#008ae6'], alpha=0.2)
# Sort out x-axis
# Demarcate months
dim = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
ax.xaxis.set_ticks(np.cumsum(dim))
ax.xaxis.set_major_formatter(FuncFormatter(dateformatter))
ax.set_xlabel(u'Date', fontsize=11)
# Sort out y-axis
ax.yaxis.set_major_formatter(FuncFormatter(timeformatter))
ax.set_ylim([55000, 86400])
ax.set_ylabel(u'Time', fontsize=11)
labels = ax.get_xticklabels()
plt.setp(labels, rotation=30, fontsize=9)
# Done
plt.show()


# In[79]:


# Sunset length
settings = []

for i in range(1, 368):
    home.date += ephem.Date(1)
    home.horizon = '0'
    start = home.next_setting(sun, use_center=False).datetime()
    home.horizon = '-0.53'
    end = home.next_setting(sun, use_center=False).datetime()
    settings.append((end - start).total_seconds())
    
ts = pd.Series(settings, index=pd.date_range('2019/1/1', periods=len(settings)))

ax = ts.plot.area(alpha=0.2)
plt.rcParams["figure.figsize"] = [9, 6]
ax.set_xlabel(u'Date', fontsize=11)
ax.set_ylabel(u'Sunset length (seconds)', fontsize=11)
ax.set_ylim([math.floor(ts.min()) - 15, math.floor(ts.max()) + 15])
# Fire
plt.show()

