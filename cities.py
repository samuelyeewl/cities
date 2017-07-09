#!/usr/bin/env python

# __cities__.py
# Outputs interesting information about the __cities__ of the world.
# City data from http://maxmind.com/app/world__cities__
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

EARTH_RADIUS = 6371
EARTH_CIRCUMFERENCE = 40075

__cities__ = []
__usstates__ = {}
__countries__ = {}


class City:
    def __init__(self, name, countrycode, population, latitude, longitude):
        temp = name.encode(sys.stdout.encoding, 'ignore')
        self.name = temp.decode(sys.stdout.encoding)
        self.countrycode = countrycode
        self.country = __countries__[countrycode.upper()]
        self.population = int(population)
        self.latitude = float(latitude)
        self.longitude = float(longitude)


def city_name(city, fullstatename=True):
    if city.country == 'United States':
        if fullstatename:
            return ('{}, {} ({}), {}'.format(city.name, __usstates__[city.us_state], city.us_state, city.country))
        else:
            return ('{}, {}, {}'.format(city.name, city.us_state, city.country))
    else:
        return ('{}, {}'.format(city.name, city.country))


def print_city(city, verbose=False, numextra=1, population=100000):
    print('=' * 50)
    print(city_name(city))
    print('-' * 50)
    print('Population: {:,}'.format(city.population))
    print('Pop Rank: {}'.format(__cities__.index(city) + 1))
    print('Coordinates: {:.4f}, {:.4f}'.format(city.latitude, city.longitude))
    if verbose:
        citydistance = [c for c in __cities__ if c.population >= population]
        for c in citydistance:
            c.dist = calc_distance(city, c)
        citydistance.sort(key=lambda city: city.dist)

        f__cities__ = citydistance[-numextra:]
        f__cities__.reverse()
        print_extra___cities__(f__cities__, 'Furthest __cities__')

        n__cities__ = citydistance[1:numextra + 1]
        print_extra___cities__(n__cities__, 'Nearest __cities__')

        p__cities__ = __cities__[__cities__.index(city) - numextra:__cities__.index(city)] \
            + __cities__[__cities__.index(city) + 1:__cities__.index(city) + numextra + 1]
        print_extra___cities__(p__cities__, 'Closest population')

    print('=' * 50)
    print('\n')


def print_extra_cities(extra___cities__, info_name):
    print('-' * 50)
    print(info_name + ':' + ' ' * (20 - len(info_name) - 1) + '(1) ' +
          city_name(extra___cities__[0], False))
    print_extra_info(extra___cities__[0])
    for idx, city in enumerate(extra___cities__[1:]):
        print(' ' * 20 + '({}) '.format(idx + 2) + city_name(city, False))
        print_extra_info(city)


def print_extra_info(city):
    print(' ' * 20 + '- Population: {:,} ({})'.format(city.population,
                                                      __cities__.index(city) + 1))
    print(' ' * 20 + '- Distance: {:,.0f}km ({:.2%})'
          .format(city.dist, city.dist / EARTH_CIRCUMFERENCE * 2))


def calc_distance(city1, city2):
    lat1 = math.radians(city1.latitude)
    lat2 = math.radians(city2.latitude)
    deltalong = math.radians(city2.longitude - city1.longitude)
    dist = math.acos(math.sin(lat1) * math.sin(lat2) + math.cos(lat1) *
                     math.cos(lat2) * math.cos(deltalong)) * EARTH_RADIUS
    return dist


def print_distance(city1, city2):
    distance = calc_distance(city1, city2)
    print('*** ' + city_name(city1, False) + ' ----- ' + city_name(city2, False) + ' ***')
    print(' ' * 4 + 'Distance: {:,.0f}km ({:.2%})'
          .format(distance, distance / EARTH_CIRCUMFERENCE * 2))
    print('\n')


def find_city(cityname, population=100000):
    l = cityname.split(', ')

    matched = [c for c in __cities__ if c.name.lower() == l[0].lower() and
               c.population > population]

    if len(l) > 1:
        country = l[-1].lower()
        matched = [c for c in matched if c.country.lower() == country or c.countrycode.lower() == country]
        if len(l) >= 3 and (country.lower() == 'united states' or country.lower() == 'us'):
            state = l[-2].upper()
            if state in __usstates__:
                matched = [c for c in matched if c.us_state.upper() == state]
            else:
                for code, name in __usstates__:
                    if state == name.upper():
                        matched == [c for c in matched if c.us_state.upper() == code.upper()]
    return matched


def __init__():
    global __cities__
    global __usstates__
    global __countries__
    with open('countrycodes.csv', 'r') as countryfile:
        csvreader = csv.reader(countryfile, delimiter=',')
        for row in csvreader:
            __countries__[row[4]] = row[7]

    with open('cities.txt', 'r', encoding='utf-8') as cityfile:
        csvreader = csv.reader(cityfile, delimiter='\t')
        next(csvreader)
        for row in csvreader:
            new_city = City(row[2], row[8], row[14], row[4], row[5])
            if new_city.country == 'United States':
                new_city.us_state = row[10]
            __cities__.append(new_city)

    with open('usstates.csv', 'r') as statesfile:
        csvreader = csv.reader(statesfile, delimiter=',')
        for row in csvreader:
            __usstates__[row[1]] = row[0]

    __cities__.sort(key=lambda city: city.population, reverse=True)


def main():
    parser = argparse.ArgumentParser(description='get some information about __cities__')
    parser.add_argument('cities', nargs='+', default=None, help='"city name[, US state, country]"')
    parser.add_argument('-v', '--verbose', action='store_true', help='display more information')
    parser.add_argument('-n', '--number', type=int, default=5, help='number of __cities__ to display if no city specified')
    parser.add_argument('-n2', '--numextra', type=int, default=1, help='number of __cities__ to display in extra info')
    parser.add_argument('-p', '--population', choices=['0', '10k', '100k', '1M'], default='100k', help='minimum population of __cities__ to search for (default: 100k)')
    args = parser.parse_args()

    if (args.population == '0'):
        args.population = 0
    elif (args.population == '10k'):
        args.population = 10000
    elif (args.population == '100k'):
        args.population = 100000
    elif (args.population == '1M'):
        args.population = 1000000

    if args.cities:
        querylist = []
        for cityname in args.cities:
            matched = find_city(cityname, args.population)
            if len(matched) == 0:
                print('Sorry, no cities with name {} found!'.format(cityname))
            querylist.extend(matched)
        for i, city in enumerate(querylist):
            print_city(city, args.verbose, args.numextra, args.population)
            for city2 in querylist[i + 1:]:
                print_distance(city, city2)

    else:
        for city in __cities__[:args.number]:
            print_city(city, args.verbose, args.numextra, args.population)


if __name__ == '__main__':
    __init__()
    main()
