#!/usr/bin/env python

# cities_to_json.py

import cities
import sys


def main():
    cities.__init__()
    infile = open(sys.argv[1], 'r')
    outfile = open("./out.json", 'w')
    lines = infile.readlines()

    outfile.write("var locations = [\n")
    for row in lines:
        c_name = row.rstrip('\n')

        found = cities.find_city(c_name, 10000)
        if len(found) == 0:
            print("Could not find city " + c_name)
            continue

        outfile.write("\t{\n")
        city = found[0]
        outfile.write('\t\t"name": "' +
                      cities.city_name(city, fullstatename=False) + '",\n')
        outfile.write('\t\t"lat": {:.4f},\n'.format(city.latitude))
        outfile.write('\t\t"long": {:.4f},\n'.format(city.longitude))
        outfile.write("\t},\n")
    outfile.write("]")


if __name__ == '__main__':
    main()
