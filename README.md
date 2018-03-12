# Red Cross Chicago Fire Risk Finder

## Tool Overview

The Red Cross Fire Risk Finder is a Red Cross tool built by Uptake Technologies that predicts the risk of fire across various neighborhoods in Chicago. Users are able to search for the fire risk score of their home and subsequently request installation of a smoke alarm from the Red Cross, free of charge.

The tool employs a predictive model to assign a fire risk score to neighborhoods in Chicago, which is calculated from the number of previous fires and the demographic and socioeconomic characteristics of the neighborhood, such as number of households and median home value among others. Each risk score is calculated and classified into a risk category (one of six) which is displayed on the tool.
<br>

## Data Sources

Data on fire occurrences throughout the city (at the block level) were received via a FOIA request to the City of Chicago Office of Emergency Management and Communication (OEMC). The tool is built upon fire occurrences from June 1, 2013 to May 31, 2017.

Household demographic, socioeconomic, and housing-related data were queried from the U.S. Census Bureau’s 2011-2015 5-year American Community Survey (ACS) household survey.

Census tract boundaries and shapefiles are based on 2010 U.S. census tract boundaries and were acquired from the City of Chicago’s Open Data Portal.

Red Cross disaster response data was provided by the Red Cross. A layer of the tool is built upon this data (filtered on fire incidents) from January 1, 2014 to June 30, 2017. The data is used for display, not modeling, purposes.


## Methodology

Fire data was cleaned appropriately and records were deduplicated and aggregated to the census tract level (see Considerations/Assumptions section) in order to create frequencies of fire occurrences across the city within the past three years.

The Google Maps API and Census Geocoder API were utilized to attain approximate latitude and longitude and 2010 census tracts, respectively, of each fire occurrence. Fires were aggregated within census tracts in order to create a model that predicts fire risk at a 2010 census tract level.

Demographic, socioeconomic, and housing-related variables were pulled from the ACS Census data sets and joined with each of the respective Cook County tracts represented in the fire occurrence data.


## Modeling

The fire occurrence data and census data at the tract level together were used to create a predictive model for fire risk within each Chicago census tract. A Generalized Linear Model Poisson Regression was employed and was fit with lasso regularization. Cross validation was utilized to train and test the model.

The outcome variable, fires per census tract, was predicted using an offset for number of households per tract to account for exposure. Many demographic, socioeconomic, and housing-related variables were used in the model and the most significant ones used to fit the model (all at the household level in each tract) were median household income, population over the age of 16 in the labor force, ratio of vacant units per total housing units, and median housing value. The final prediction was normalized by the number of households in the tract to calculate the corresponding risk score. Out-of-sample predictions were used to calculate the risk score.

Scores were assigned to six bins based on the values (displayed in the user interface). Users are able to search various addresses within Chicago and receive the corresponding risk level.

## Considerations/Assumptions

The fire dataset included occurrence of fire at the block level and was not categorized by commercial or residential fire. Three types of fire ‘event types’ were included in the fire dataset without specification of the differences. Thus, all fires reported were initially treated the same. In order to account for the possible over-reporting of fires (or repeat fire reporting for the same fire, represented by more than one row in the dataset), multiple rows with the same fire block address on the same day were assumed to correspond to the same fire, regardless of ‘event type’.

The Google Maps API and Census Geocoder API were utilized to get latitude and longitude and census tract information for the various fire locations in the dataset. Both of these APIs have daily limitations on the number of API calls, so the data may need to be split up into batches to query the APIs on multiple days. The Google API requires an API key.

Census variables were queried from the U.S. Census Bureau’s 2011-2015 5-year American Community Survey (ACS) household survey using the IPUMS website. The static dataset is posted on Git and filtered to all census tracts in Cook County, Illinois.

The predictions and fire risk scores included within this tool have been predetermined using the model. Because the fire dataset is not updated and the census data is static, the predictions are static as well. The model is not ingested with new data. Results should be interpreted with the perspective that this model was fit in September 2017 with fire data from 2013-2017.

## Dependencies/Packages

**Python 3**
- Packages: Pandas, Numpy

**R**
- Packages: glmnet

**JavaScript**
- Packages: Leaflet, JQuery, leaflet-pip

**Google Maps API**
- Resources available [here](https://developers.google.com/maps/)

**Census Geocoder API**
- Resources available [here](https://www.census.gov/geo/maps-data/data/geocoder.html)

## Data preparation (skip this section if just running demo server)

Because of the sensitivity of the fire dataset, Red Cross will not be publishing the OEMC fire dataset. In order to rerun, remodel, or build upon this tool, users will need to request the data on their own. Once the data is obtained, the instructions below say how to rerun/update the model (though slight customizations may be needed).  However, if you just want to run the app with the demo data included in this repository, you can skip the data preparation steps

#### 1. Run data preparation steps using the CSV of fire data
```
data_prep/prep_data.py
```
- This file initiates and completes all code for data cleaning, preparation, and joining needed for the fire data and the census data.

#### 2. Run modeling code with the resulting CSV
```
model/GLM_fire_model.R
```
- This file runs the modeling code with the optimal set of predictors, calculates predictions, and outputs the appropriate risk score for each of the tracts in the dataset.

#### 3. Run mapping file with the model outputs
```
data_prep/map_data.R
```
- This file loads the model results and creates the geojson files used in the final tool.

## Running the app

To launch the fire risk app on a web server, do:

```
cd red_cross/app
python -m SimpleHTTPServer 8888
```
or

```
cd red_cross/app
python3 -m http.server
```
- The files and scripts needed to run the tool in a browser are stored in the "app" folder. The tool can be launched and tested on a local machine using Python’s built-in HTTP server. The app will be made available at "localhost:8888".
