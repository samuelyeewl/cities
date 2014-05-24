#!/usr/bin/env python

# cities.py
# Outputs interesting information about the cities of the world.
# City data from http://maxmind.com/app/worldcities
# Country code data from http://datahub.io
# US state codes from http://statetable.com
#
# By Samuel Yee, 2014
# 
# Disclaimer: The author of this script bears no responsibility for any
# inaccuracies in the data.

import csv
import sys, argparse 
import math

EARTH_RADIUS=6371
EARTH_CIRCUMFERENCE=40075

parser = argparse.ArgumentParser(description='get some information about cities')
parser.add_argument('cities', nargs='+', default=None, help='"city name[, US state, country]"')
parser.add_argument('-v', '--verbose', action='store_true', help='display more information')
parser.add_argument('-n', '--number', type=int, default=5, help='number of cities to display if no city specified')
parser.add_argument('-n2', '--numextra', type=int, default=1, help='number of cities to display in extra info')
parser.add_argument('-p', '--population', choices=['0', '10k', '100k', '1M'], default='100k', help='minimum population of cities to search for (default: 100k)')
args = parser.parse_args()

if (args.population == '0'):
    args.population = 0
elif (args.population == '10k'):
    args.population = 10000
elif (args.population == '100k'):
    args.population = 100000
elif (args.population == '1M'):
    args.population = 1000000


class City:
    def __init__(self, name, countrycode, population, latitude, longitude):
        temp = name.encode(sys.stdout.encoding, 'ignore')
        self.name = temp.decode(sys.stdout.encoding)
        self.countrycode = countrycode
        self.country = countries[countrycode.upper()]
        self.population = int(population)
        self.latitude = float(latitude)
        self.longitude = float(longitude)

def city_name(city, fullstatename=True):
    if city.country == 'United States':
        if fullstatename:
            return ('{}, {} ({}), {}'.format(city.name, usstates[city.us_state], city.us_state, city.country))
        else:
            return ('{}, {}, {}'.format(city.name, city.us_state, city.country))
    else:
        return ('{}, {}'.format(city.name, city.country))

def print_city(city, verbose=args.verbose):
    print('='*50)
    print(city_name(city))
    print('-'*50)
    print('Population: {:,}'.format(city.population))
    print('Pop Rank: {}'.format(cities.index(city)+1))
    print('Coordinates: {}, {}'.format(city.latitude, city.longitude))
    if args.verbose:
        citydistance = [c for c in cities if c.population >= args.population]
        for c in citydistance:
            c.dist = calc_distance(city, c)
        citydistance.sort(key=lambda city: city.dist) 
        
        fcities = citydistance[-args.numextra:]
        fcities.reverse()
        print_extra_cities(fcities, 'Furthest cities')

        ncities = citydistance[1:args.numextra+1]
        print_extra_cities(ncities, 'Nearest cities')

        pcities = cities[cities.index(city)-args.numextra:cities.index(city)]+cities[cities.index(city)+1:cities.index(city)+args.numextra+1]
        print_extra_cities(pcities, 'Closest population')

    print('='*50)
    print('\n')

def print_extra_cities(extra_cities, info_name):
    print('-'*50)
    print(info_name+':'+' '*(20-len(info_name)-1) + '(1) ' + city_name(extra_cities[0], False))
    print_extra_info(extra_cities[0])
    for idx, city in enumerate(extra_cities[1:]):
        print(' '*20 + '({}) '.format(idx+2) + city_name(city, False))
        print_extra_info(city)

def print_extra_info(city):
    print(' '*20 + '- Population: {:,} ({})'.format(city.population, cities.index(city)+1))
    print(' '*20 + '- Distance: {:,.0f}km ({:.2%})'.format(city.dist, city.dist/EARTH_CIRCUMFERENCE*2))

def calc_distance(city1, city2):
    lat1 = math.radians(city1.latitude)
    lat2 = math.radians(city2.latitude)
    deltalong = math.radians(city2.longitude - city1.longitude)
    dist = math.acos(math.sin(lat1)*math.sin(lat2) + math.cos(lat1)*math.cos(lat2) * math.cos(deltalong)) * EARTH_RADIUS
    return dist
    
def print_distance(city1, city2):
    distance = calc_distance(city1, city2)
    print('*** ' + city_name(city1, False) + ' ----- ' + city_name(city2, False) + ' ***')
    print(' '*4 + 'Distance: {:,.0f}km ({:.2%})'.format(distance, distance/EARTH_CIRCUMFERENCE*2))
    print('\n')

def find_city(cityname):
    l = cityname.split(', ')
    matched = [c for c in cities if c.name.lower() == l[0].lower() and c.population > args.population]

    if len(l) > 1:
        country = l[-1].lower()
        matched = [c for c in matched if c.country.lower() == country or c.countrycode.lower() == country]
        if len(l) >= 3 and (country.lower() == 'united states' or country.lower() == 'us'):
            state = l[-2].upper()
            if state in usstates:
                matched = [c for c in matched if c.us_state.upper() == state]
            else:
                for code, name in usstates:
                    if state == name.upper():
                        matched == [c for c in matched if c.us_state.upper() == code.upper()]
    return matched


cities = []
countries = {}
usstates = {}

with open('countrycodes.csv', 'r') as countryfile:
    csvreader = csv.reader(countryfile, delimiter=',')
    for row in csvreader:
        countries[row[4]] = row[7]

with open('cities.txt', 'r', encoding='iso_8859_1') as cityfile:
    csvreader = csv.reader(cityfile, delimiter=',')
    next(csvreader)
    for row in csvreader:
        new_city = City(row[2], row[0], row[4], row[5], row[6])
        if new_city.country=='United States':
            new_city.us_state = row[3]
        cities.append(new_city)

with open('usstates.csv', 'r') as statesfile:
    csvreader = csv.reader(statesfile, delimiter=',')
    for row in csvreader:
        usstates[row[1]] = row[0]

cities.sort(key=lambda city: city.population, reverse=True)

if args.cities:
    querylist = []
    for cityname in args.cities:
        matched = find_city(cityname)
        if len(matched) == 0:
            print('Sorry, no cities with name {} found!'.format(cityname))
        querylist.extend(matched)
    for i, city in enumerate(querylist):
        print_city(city)
        for city2 in querylist[i+1:]:
            print_distance(city, city2)

else:
    for city in cities[:args.number]:
        print_city(city)
