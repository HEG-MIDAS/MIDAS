#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "David Nogueiras Blanco, and Amir Alwash"
__copyright__ = ""
__credits__ = ["David Nogueiras Blanco, Amir Alwash"]
__license__ = ""
__version__ = "1.0.1"
__maintainer__ = "David Nogueiras Blanco"
__email__ = "david.nogueiras-blanco@hesge.ch"
__status__ = "Development"

import requests
import json

# Define here all the elements of the header
# Replace username by the username you use on the website
# Replace token by a token that you create on the website
headers = {
    'Authorization': 'Midas admin 4yQ[[?$b(7O&FFv2,v:R',
    'Content-Type': 'application/json'
}

print("------------------ GET EXAMPLES ------------------\n")

# Get example getting the status of the website
print("---- Status ----\n")
response = requests.get("http://gexplore.ch/api/status", headers=headers)
print(response.content,"\n")

# Get example getting data about the sources
print("---- Sources ----\n")
response = requests.get("http://gexplore.ch/api/sources", headers=headers)
print(response.content,"\n")

print("------------------ POST EXAMPLES ------------------\n")

data = {
    "sources": ["sabra"],
    "stations": ["necker"]
}

# Post example for searching data
print("---- Filter ----\n")
response = requests.post("http://gexplore.ch/api/filter/", headers=headers, data=json.dumps(data))
print(response.content,"\n")

data = {
    "sources": ["sabra"],
    "stations": ["necker"],
    "parameters": ["pm2_5"],
    "start_date": "2022-7-18 00:00:00",
    "end_date": "2022-7-18 23:59:00"
}

# Post example for searching data
print("---- Search ----\n")
response = requests.post("http://gexplore.ch/api/search/", headers=headers, data=json.dumps(data))
print(response.content,"\n")
