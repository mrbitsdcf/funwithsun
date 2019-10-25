#!/usr/bin/env python3

import json
import turtle
import urllib.request
import turtle
import time


url = "http://api.open-notify.org/astros.json"
response = urllib.request.urlopen(url)
result = json.loads(response.read())
print("People in space:", result['number'])
people = result['people']

for p in people:
    print(p['name'], "is in", p['craft'])

url = "http://api.open-notify.org/iss-now.json"
response = urllib.request.urlopen(url)
result = json.loads(response.read())

location = result['iss_position']
lat = location['latitude']
lon = location['longitude']

print("Latitude:", lat)
print("Longitude:", lon)

screen = turtle.Screen()
screen.setup(720, 360)
screen.setworldcoordinates(-180, -90, 180, 90)
screen.bgpic('map.gif')

iss = turtle.Turtle()
screen.register_shape('iss2.gif')
iss.shape('iss2.gif')
iss.setheading(90)
iss.penup()

iss.goto(float(lon), float(lat))

lat = -23.25
lon = -46.66

location = turtle.Turtle()
location.penup()
location.color('yellow')
location.goto(lon, lat)
location.dot(5)
location.hideturtle()

url = 'http://api.open-notify.org/iss-pass.json?lat=' + str(lat) + '&lon=' + str(lon)
response = urllib.request.urlopen(url)
result = json.loads(response.read())

over = result['response'][1]['risetime']
location.write(time.ctime(over))
