# Copyright © 2017 American Red Cross
# 
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the “Software”), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import csv
import pandas as pd
import numpy as np
import requests
from datetime import datetime
from dateutil.parser import parse
from datetime import timedelta
import json
import requests
import re


def extract_data(census_data, census_df):
  	#reformat the ACS dataset

    copy_vars = ['GISJOIN','YEAR','STATE','STATEA','COUNTY','COUNTYA','TRACTA']
    census_df[copy_vars] = census_data[copy_vars]

    census_df['total_males'] = census_data['ADKLE002']
    census_df['total_females'] = census_data['ADKLE026']
    census_df['total_pop'] = census_data['ADKWE001']
    census_df['pop_above_25'] = census_data['ADMZE001']
    census_df['educ_pop_above_25_HS_or_above'] = census_data[['ADMZE017','ADMZE018','ADMZE019','ADMZE020','ADMZE021','ADMZE022','ADMZE023','ADMZE024','ADMZE025']].sum(axis=1)
    census_df['educ_pop_above_25_bach_or_above'] = census_data[['ADMZE022','ADMZE023','ADMZE024','ADMZE025']].sum(axis=1)
    census_df['med_income_past_12_month'] = census_data['ADNKE001']
    census_df['num_HH'] = census_data['ADPZE002']
    census_df['total_fam_HH_householder'] = census_data['ADLRE004']
    census_df['total_nonfam_HH_householder'] = census_data['ADLRE025']
    census_df['total_pop_over16'] = census_data['ADPIE001']
    census_df['total_pop_over16_labor_force'] = census_data['ADPIE002']
    census_df['total_pop_over16_NOT_labor_force'] = census_data['ADPIE007']
    census_df['total_housing_units'] = census_data['ADPYE001']
    census_df['total_occupied_housing_units'] = census_data['ADPZE002']
    census_df['total_vacant_housing_units'] = census_data['ADPZE003']
    census_df['av_HH_size_total'] = census_data['ADQFE001']
    census_df['av_HH_size_owner'] = census_data['ADQFE002']
    census_df['av_HH_size_renter'] = census_data['ADQFE003']
    census_df['med_yr_built'] = census_data['ADQTE001']
    census_df['med_rent'] = census_data['ADRKE001']
    census_df['med_house_value_owner'] = census_data['ADRWE001']

    census_df = impute(census_df)
    census_df = household_level(census_df)

    return census_df


def impute(census_df):
  	#impute missing values for ACS data

    col_impute = ['total_males','total_females','total_pop','pop_above_25',
    'educ_pop_above_25_HS_or_above','educ_pop_above_25_bach_or_above','med_income_past_12_month',
    'num_HH','total_fam_HH_householder','total_nonfam_HH_householder','total_pop_over16',
    'total_pop_over16_labor_force','total_pop_over16_NOT_labor_force',
    'total_housing_units','total_occupied_housing_units','total_vacant_housing_units',
    'av_HH_size_total','av_HH_size_owner', 'av_HH_size_renter','med_yr_built','med_rent',
    'med_house_value_owner']

    census_df.loc[census_df['num_HH'] == 0 , col_impute] = 0
    census_df[col_impute] = census_df[col_impute].fillna(census_df[col_impute].mean())

    return census_df
  

def household_level(census_df):
  	#create variables at the household level per tract

    census_df['male_per_HH'] = per_unit_HH('total_males', census_df)
    census_df['female_per_HH'] = per_unit_HH('total_females', census_df)
    census_df['educ_HS_per_HH'] = per_unit_HH('educ_pop_above_25_HS_or_above', census_df)
    census_df['educ_bach_per_HH'] = per_unit_HH('educ_pop_above_25_bach_or_above', census_df)
    census_df['median_pop_per_HH'] = per_unit_HH('total_pop', census_df)
    census_df['famHH_per_HH'] = per_unit_HH('total_fam_HH_householder', census_df)
    census_df['non-famHH_per_HH'] = per_unit_HH('total_nonfam_HH_householder', census_df)
    census_df['pop_over16_per_HH'] = per_unit_HH('total_pop_over16', census_df)
    census_df['pop_over16_labor_force_per_HH'] = per_unit_HH('total_pop_over16_labor_force', census_df)
    census_df['pop_over16_NOT_labor_force_per_HH'] = per_unit_HH('total_pop_over16_NOT_labor_force', census_df)

    census_df['occupied_HH_per_total_housing_units'] = census_df['total_occupied_housing_units']/census_df['total_housing_units']
    census_df['vacancy_per_total_housing_unit'] = census_df['total_vacant_housing_units']/census_df['total_housing_units']
    census_df.fillna(0, inplace = True)

    return census_df
  

def per_unit_HH(column, census_df):
  	#helper function to create a per unit variable at the household level

    per_unit_HH = census_df[column]/census_df['num_HH']
    
    return per_unit_HH
  

def prep_census(census_data):
  	#initiates all the data cleaning functions

    census_df = pd.DataFrame()
    census_df = extract_data(census_data, census_df)
    
    return census_df
