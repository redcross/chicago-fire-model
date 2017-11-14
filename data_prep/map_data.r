library(data.table)
library(geojsonio)
library(rgdal)
library(jsonlite)

rm(list=ls())

# ILLINOIS CENSUS TRACTS
ftract <- "./data/chicago_tracts_clipped.geojson"
censusTracts <- readOGR(ftract, "OGRGeoJSON", stringsAsFactors = FALSE)

# RISK SCORE DATA
friskscore <- "./data/fire_model_data_output.csv"
riskScore <- fread(friskscore)
riskScore$fire_score_bin_orig <- riskScore$fire_score_bin
fireScoreBins <- c(.0125, .0250, .0375, .0500)
riskScore[, fire_score_bin := dplyr::case_when(
  riskScore$fire_score < fireScoreBins[1] ~ 0
  , riskScore$fire_score < fireScoreBins[2] ~ 1
  , riskScore$fire_score < fireScoreBins[3] ~ 2
  , riskScore$fire_score < fireScoreBins[4] ~ 3
  , TRUE ~ 4
)]

riskScore[, TRACTA := as.character(TRACTA)]
riskScore[nchar(TRACTA) == 5, TRACTA := paste0("0", TRACTA)]

# Tracts in the risk score file but not the census file
setdiff(riskScore$TRACTA, censusTracts@data$tractce10)
# Tracts in the census file but not the risk score file
setdiff(censusTracts@data$tractce10, riskScore$TRACTA)

# MERGE
censusTracts@data <- data.frame(
  censusTracts@data, 
  riskScore[match(censusTracts@data$tractce10, riskScore$TRACTA)
            , c("TRACTA", "NAME_E", "prediction", "fire_score"
                , "fire_score_bin", "fire_score_bin_orig")]
  )

# RED CROSS RESPONSES
fRedCrossResponses <- "./data/red_cross_responses_tract.csv"
redCrossResponses <- fread(fRedCrossResponses)
redCrossResponses <- redCrossResponses[, c("CensusTract", "responses_per_tract")]

summary(redCrossResponses$responses_per_tract)

table(nchar(redCrossResponses$CensusTract))
ct <- redCrossResponses$CensusTract
ct <- as.character(ct)
hasdec <- stringi::stri_detect_fixed(ct, ".")
ct[!hasdec] <- paste0(ct[!hasdec], "00")
table(nchar(ct[hasdec]))
table(nchar(ct[!hasdec]))
ct[hasdec & nchar(ct)==6] <- paste0("0", ct[hasdec & nchar(ct)==6])
ct[!hasdec & nchar(ct)==5] <- paste0("0", ct[!hasdec & nchar(ct)==5])
ct <- stringi::stri_replace_all_fixed(ct, ".", "")
table(nchar(ct))
redCrossResponses$new_tract <- as.character(ct)


setdiff(redCrossResponses$new_tract, tract_fire@data$tractce10)
setdiff(tract_fire@data$tractce10, redCrossResponses$new_tract)

tract_fire@data <- data.frame(
  tract_fire@data, 
  redCrossResponses[match(tract_fire@data$tractce10, redCrossResponses$new_tract), ]
)
summary(tract_fire@data$responses_per_tract)

geojsonio::geojson_write(
  tract_fire, 
  file = "./data/tract_fire_scores_responses.geojson")



