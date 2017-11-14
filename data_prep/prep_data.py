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
import csv
import re

from data_cleaning import *
from geocode import *
from census_demog import *
from match_data import *
from census_data_prep import *

if __name__ == "__main__":

    #fire dataset is not uploaded to Git due to sensistivity. In order to run the
    #code and model, a user will need to obtain the data from the Chicago OEMC.
    df = pd.read_csv("data/CHICAGO_FIRES_FOIA_FA17-1004.csv")
    df = clean(df)
    df = fire_date_time(df)

    #cleaned dataset with all addresses grouped by unique day of fire
    df = deduplicate_fire(df)
    df_unique_geo = geocode(df)
    data_to_model = combine_data(df, df_unique_geo)

    #variables from 2011-2015 5-year American Community Survey (ACS) household survey
    census_data = pd.read_csv("data/nhgis_cook_county_tracts.csv")
    data_from_census = prep_census(census_data)

    #dataset to be used to model fire risk predictions and scores
    data_to_model = data_to_model.merge(data_from_census, how='left', left_on = data_to_model['census_tract'], right_on = data_from_census['TRACTA']/100)
    data_to_model.to_csv('data/data_to_model.csv')
