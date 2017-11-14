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
