import csv
import pandas as pd
import numpy as np
import requests
from datetime import datetime
from dateutil.parser import parse
from datetime import timedelta
import re

def clean(df):
	#apply various data cleaning steps to the addresses in the dataset

    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.columns = ['Event_ID','Date_time','Type_code','Type_description','Block_address']
    df = df[df['Block_address'].notnull()]
    df = df[df['Date_time'].notnull()]
    df['Block_address_CLEAN'] = df['Block_address']
    df['Block_address_CLEAN'] = df['Block_address_CLEAN'].str.replace(' Blk ',' ')
    df['Block_address_CLEAN'] = df['Block_address_CLEAN'].str.upper()
    df['Block_address_CLEAN'] = df['Block_address_CLEAN'].str.split('\(').str[0]
    df['Block_address_CLEAN'] = df['Block_address_CLEAN'].str.strip()

    df['Block_address_CLEAN'] = df['Block_address_CLEAN'].apply(consistent_address)
    df['Block_address_CLEAN'] = df['Block_address_CLEAN'] + ", CHICAGO, IL"
    
    return df

  
def consistent_address(address):
	#ensure consistency in address syntax
    
    address = re.sub(r'\bAV\b', 'AVENUE', address)
    address = re.sub(r'\bBL\b', 'BLOCK', address)
    address = re.sub(r'\bBLK\b', 'BLOCK', address)
    address = re.sub(r'\bST\b', 'STEET', address)
    address = re.sub(r'\bPL\b', 'PLACE', address)
    address = re.sub(r'\bPKWY\b', 'PARKWAY.', address)
    address = re.sub(r'\bMARTIN LUTHER KIN\b', 'MARTIN LUTHER KING DRIVE', address)
    
    return address

  
def fire_date_time(df):
	#convert to datatype date-time and parse the values

    df = df[df['Date_time'].str.contains('Entrydate and Time\r') == False]
    df = df[~df['Date_time'].isin(['Entrydate and Time\r'])]
    df['Date_time'] =  pd.to_datetime(df['Date_time'], format='%m/%d/%Y %H:%M:%S')
    df['Fire_year'] = pd.DatetimeIndex(df['Date_time']).year
    df['Fire_month'] = pd.DatetimeIndex(df['Date_time']).month
    df['Fire_day'] = pd.DatetimeIndex(df['Date_time']).day
    
    return df

  
def deduplicate_fire(df):
    #deduplicate fires on the same day at the same location

    df = df.groupby(['Block_address_CLEAN','Fire_year','Fire_month','Fire_day'], as_index=False).count()
    df['total_fires_day'] = df['Event_ID']
    df =  df[['Block_address_CLEAN', 'Fire_year', 'Fire_month', 'Fire_day']]
    
    return df
