library(glmnet)
library(mltools)

dat = read.csv("data/data_to_model.csv")
attach(dat)
names(dat)

#find tracts that have households
dat = dat[apply(dat[c('num_HH')],1,function(z) !any(z==0)),]

#scale and standardize income variable
dat$med_income_past_12_month = (dat$med_income_past_12_month/10000 - mean(dat$med_income_past_12_month/10000)) / sd(dat$med_income_past_12_month/10000)

col_to_transform = c('male_per_HH',
                     'female_per_HH',
                     'educ_HS_per_HH',
                     'educ_bach_per_HH',
                     'median_pop_per_HH',
                     'famHH_per_HH',
                     'non-famHH_per_HH',
                     'pop_over16_labor_force_per_HH',
                     'pop_over16_NOT_labor_force_per_HH',
                     'occupied_HH_per_total_housing_units',
                     'vacancy_per_total_housing_unit',
                     'av_HH_size_owner',
                     'av_HH_size_renter',
                     'med_yr_built',
                     'med_rent',
                     'med_house_value_owner')

#standardize other variables for modeling
dat[col_to_transform] = scale(dat[col_to_transform], center = TRUE, scale = TRUE)
dat$num_HH = dat$num_HH
dat$total_pop = dat$total_pop

#select the independent variables; account for obvious collinearity
x = as.matrix(dat[c('med_income_past_12_month',
                    #'male_per_HH',
                    'female_per_HH',
                    #'educ_HS_per_HH',
                    'educ_bach_per_HH',
                    'median_pop_per_HH',
                    'famHH_per_HH',
                    #'non-famHH_per_HH',
                    'pop_over16_labor_force_per_HH',
                    #'pop_over16_NOT_labor_force_per_HH',
                    #'occupied_HH_per_total_housing_units',
                    'vacancy_per_total_housing_unit',
                    'av_HH_size_owner',
                    'av_HH_size_renter',
                    'med_yr_built',
                    'med_rent',
                    'med_house_value_owner')])

#select the dependent variable
y = as.matrix(dat[c('fire_per_tract')])

#select the offset
hh_offset = dat[c('num_HH')]
hh_offset = log(hh_offset)
hh_offset = as.matrix(hh_offset)

#fit a glmnet poisson regression model
fit = glmnet(x, y, family=c('poisson'), offset=hh_offset, alpha=1)

#cross validation; select lambda
cv.fit = cv.glmnet(x, y, family=c('poisson'), alpha=1, nfolds=5)

#coefficients used to fit
coef(cv.fit)

#cross validated MSE
cv.fit
cv.fit$cvm

#corresponding lambda values
cv.fit$lambda

#plot
plot(cv.fit)
best.lambda = cv.fit$lambda.min
best.lambda

#predict
prediction = predict(cv.fit,x,s=best.lambda,type="response",newoffset=hh_offset)
plot(prediction,y, xlim = c(0, 160), ylim = c(0, 160))
dat$prediction = prediction

#risk score
dat$fire_score = prediction/dat$num_HH

#histogram of predictions
#hist(prediction, breaks = 5)
#hist(dat$fire_score)

#write to a csv to be used for the interface
write.csv(dat, file = "data/fire_model_data_output.csv")
