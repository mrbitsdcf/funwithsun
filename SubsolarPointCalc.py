#!/usr/bin/env python
# coding: utf-8

import ephem
import sys
from datetime import datetime, timedelta


def datetime_range(start=None, end=None):
    span = end - start
    for i in range(span.days + 1):
        yield start + timedelta(days=i)


if len(sys.argv) != 4:
    print('''
Argumentos faltando
Uso:
    ./SubsolarPointCalc.py latitude longitude ano
    ./SubsolarPointCalc.py -23.5 -46.6 2019
        ''')
    sys.exit(1)


latitude = sys.argv[1]
longitude = sys.argv[2]
year = int(sys.argv[3])

home = ephem.Observer()

home.lat = str(latitude)
home.lon = str(longitude)

sun = ephem.Sun()
sun.compute(home)

for date in datetime_range(start=datetime(year, 1, 1), end=datetime(year, 12, 31)):
    home.date = date.strftime('%Y-%m-%d')
    rising = home.previous_rising(sun).datetime()
    rising_altitude = str(sun.alt)
    transit = home.next_transit(sun).datetime()
    transit_altitude = str(sun.alt)
    setting = home.next_setting(sun).datetime()
    setting_altitude = str(sun.alt)

    if transit_altitude > '89':
        print('Found data for date {0}'.format(date.strftime('%Y-%m-%d')))
        print('Sunrise is at {:02}:{:02}:{:02}'.format(rising.hour - 3, rising.minute, rising.second))
        print('Local noon is at {:02}:{:02}:{:02}'.format(transit.hour - 3, transit.minute, transit.second))
        print('Sun Altitude at Local noon is: {0}'.format(transit_altitude))
        print('Sunset is at {:02}:{:02}:{:02}'.format(setting.hour - 3, setting.minute, setting.second))
        print
