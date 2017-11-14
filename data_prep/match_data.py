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

def combine_data(df, df_unique_geo):

    #all addresses with the lat, lng, and census tract for each row in the dataset
    df = df.merge(df_unique_geo, how='left', left_on = df['Block_address_CLEAN'], right_on = df_unique_geo['Address'])

    #all fires aggregated per census tract
    fires_per_tract = df['census_tract'].value_counts()
    fires_per_tract_df = pd.DataFrame({'tract':fires_per_tract.index, 'fire_per_tract':fires_per_tract.values})
    df = df.merge(fires_per_tract_df, how='left', left_on = df['census_tract'], right_on = fires_per_tract_df['tract'])

    #all unique tracts with the aggregated number of fires in that tract
    df = df.drop_duplicates(subset="census_tract", keep='first')

    return df
