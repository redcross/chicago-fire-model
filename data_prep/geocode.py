import csv
import pandas as pd
import numpy as np
import requests
from datetime import datetime
from dateutil.parser import parse
from datetime import timedelta
import json
import requests
from censusgeocode import CensusGeocode


def geocode(df):
  
  	#create a datatframe with unique addresses to geocode
    unique_address_df = df['Block_address_CLEAN'].drop_duplicates().reset_index(drop=True)
    unique_address_df.columns = ["Address"]
    unique_address_df = unique_address_df.to_frame('Address')

    #get the latitude and longitude for each unique fire occurence
    unique_address_df['lat_lng']= unique_address_df['Address'].apply(lambda x: get_lat_lng(x))
    unique_address_df['lat'] = unique_address_df['lat_lng'].str[0]
    unique_address_df['lng'] = unique_address_df['lat_lng'].str[1]

    #get the Census Tract for each unique fire occurence
    unique_address_df['census_tract']= unique_address_df['lat_lng'].apply(lambda x: get_census_tract(x))
    
    return unique_address_df


def get_lat_lng(address):
    #helper function that uses the GoogleMaps API to get latitude and longitude (daily rate limits)

    url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + str(address) + "&key=INSERT_KEY_HERE"
    results = requests.get(url)
    results = results.json()
    if len(results["results"]) > 0:
        lat = results["results"][0]["geometry"]["location"]["lat"]
        lng = results["results"][0]["geometry"]["location"]["lng"]
        return lat, lng

      
def get_census_tract(lat_lng):
    #helper function that uses the Census Geocoder API to get Census Tract from latitude and longitude (daily rate limits)  

    census_tract = ''
    if lat_lng is not None:
        cg = CensusGeocode()
        lat = lat_lng[0]
        lng = lat_lng[1]
        result = cg.coordinates(x=lng, y=lat)

        if len(result) > 0 and 'Census Tracts' in result[0] and len(result[0]['Census Tracts']) > 0:
            if 'TRACT' in result[0]['Census Tracts'][0]:
                census_tract = int(result[0]['Census Tracts'][0]['TRACT'])/100

    return census_tract
