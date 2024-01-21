
##################################################
#  Monte Carlo Psychrotolerant Sporeformer Simulation v3.0
##################################################
## Project: Dairy Spoilage Model
## Script purpose: Simulate spore growth for half gallon samples of milk over a given
##                 number of days.
## Date:  October 01, 2019
## V3.0 by: Mike Phillips, Cornell University, mdp38@cornell.edu
##
## Description:
## This script simulates the growth of spores in half gallon samples of milk 
## over a specified number of days.  It uses different growth models (Buchanan, 
## Baranyi, Gompertz) to calculate the log10N count based on the growth 
## parameters.
## 
## The script imports data from input files (frequency, growth parameters, 
## initial counts) and generates simulated data.
## It then calculates the mean bacteria count per day and the percentage of 
## spoiled samples on each day.
##################################################
## Notes: Version  3.0 adds a series of stages to the temperature
## This can be used to model situations with varying temps, e.g. farm storage, 
#         transportation trucks, and retail refrigerators might
#         have different temperatures and this allows a more accurate
#         estimation of real world conditions. 
##################################################




#use a seed value for reproducibility
seed_value = 42;
set.seed(seed_value)


# Modelng Functions   -----
##muAtNewTemp
#Purpose: Calculate the new mu parameter at new temperature. 
#Params:  newTemp: the new temperature for which we calculate mu
#         oldMu: the previous mu value to adjust
#         oldTemp: the temperature corresponding to previous mu
#         T0:    Parameter used to calculate new mu
muAtNewTemp <- function(newTemp, oldMu, oldTemp = 6, T0 = -3.62) {
  numerator <- newTemp - T0
  denom <- oldTemp - T0
  newMu <- ((numerator / denom)^2) * oldMu
  
  return(newMu)
}

##lagAtNewTemp
#Purpose: Calculate the new lag parameter at new temperature.
#Params:  newTemp: the new temperature for which we calculate lag
#         oldLag: the previous lag value to adjust
#         oldTemp: the temperature corresponding to previous lag
#         T0:    Parameter used to calculate new lag
lagAtNewTemp <- function (newTemp, oldLag, oldTemp = 6, T0 = -3.62) {
  numerator <- oldTemp -T0
  denom <- newTemp - T0
  newLag <- ( (numerator / denom)^2) * oldLag
  return(newLag)
}
#Growth Models
# To understand the equations and parameters see, for example,
# https://www.sciencedirect.com/science/article/abs/pii/S0740002097901258
buchanan_log10N = function(t,lag,mumax,LOG10N0,LOG10Nmax){
  ans <- LOG10N0 + 
          (t >= lag) * 
          (t <= (lag + (LOG10Nmax - LOG10N0) * log(10)/mumax)) * 
          mumax * (t - lag)/log(10) + (t >= lag) * 
          (t > (lag + (LOG10Nmax - LOG10N0) * log(10)/mumax)) * 
          (LOG10Nmax - LOG10N0)
  return(ans)
}
gompertz_log10N = function(t,lag,mumax,LOG10N0,LOG10Nmax) {
  ans <- LOG10N0 + (LOG10Nmax - LOG10N0) * exp(-exp(mumax * exp(1) * 
          (lag - t)/((LOG10Nmax - LOG10N0) * log(10)) + 1))
  return(ans)
}
baranyi_log10N = function(t,lag,mumax,LOG10N0,LOG10Nmax) {
  ans <- LOG10Nmax + log10((-1 + exp(mumax * lag) + exp(mumax * 
        t))/(exp(mumax * t) - 1 + exp(mumax * lag) * 10^(LOG10Nmax - LOG10N0)))
  return(ans)
}

#Function to calculate log10N
#Wrapper function that calls the proper model
#Purpose: This implements the chosen growth model
log10N_func <- function(t, lag, mumax, LOG10N0, LOG10Nmax, 
                        model_name="buchanan") {
  if (model_name == "buchanan") {
    return(buchanan_log10N(t, lag, mumax, LOG10N0, LOG10Nmax) )
  }
  else if(model_name == 'baranyi') {
    return(baranyi_log10N(t, lag, mumax, LOG10N0, LOG10Nmax) )
  }
  else if(model_name == 'gompertz') {
    return(gompertz_log10N(t, lag, mumax, LOG10N0, LOG10Nmax) )
  }
  else {
    stop(paste0(model_name, " is not a valid model name. Must be one of 
                buchanan, baranyi, gompertz"))
  }
}

# Data frame creation and setup   ----
#Set up data frame to store count at each day
#Size is for n_sim bulk tanks, n_half_gal half gallon lots, n_day days
n_sim <-1000. #1000 is for testing and exploring, experiments require > 100k
n_halfgal <- 10
n_day <- 24
start_day <- 1

#Repeat each element of the sequence 1..n_sim.Bulk tank data (MC runs)
BT <- rep(seq(1, n_sim), each = n_halfgal * n_day)
#Repeat the whole sequences times # of times
half_gal <- rep(seq(1, n_halfgal), times = n_day * n_sim)
#Vector of FALSE
AT <- vector(mode="logical", n_sim * n_halfgal * n_day)
#Repeat the days for each simulation run
day <- rep(
           rep(seq(start_day, start_day + n_day-1), 
            each = n_halfgal), 
  times = n_sim)
count <- vector(mode = "logical", n_sim * n_halfgal * n_day)

#matrix with columns:
#  BT   half_gal    AT    day   count
data <- data.frame(BT, half_gal, AT, day, count)

#Now import the data from our input files and begin filling in our data frames
#input files
frequency_file <- "Frequency.csv"
growth_file <- "GrowthParameters.csv"
init_file <- "InitialCountsMPN.csv"

#Import frequency data and get the rpoB allelic type
freq_import <- read.csv(frequency_file, stringsAsFactors = FALSE, header = TRUE)
freq_data = freq_import$rpoB.allelic.type

#Import growth parameter data
growth_import <-read.csv(growth_file, stringsAsFactors = FALSE)

#Import initial count logMPN data
initialcount_import <- read.csv(init_file, stringsAsFactors = FALSE)
#MPN Column
initialcount_data = initialcount_import[,3]
#LOG MPN Column
initialcountlog_data = initialcount_import[,4]

# Calculate samples used in the monte carlo   ----

#Now sample the MPN distributions and the temperature distribution
#Sample logMPN from normal distribution
#Note these distributions are estimated from collected farm data
logMPN_mean <- c(-0.7226627)
logMPN_sd <- c(.9901429)
logMPN_samp = rnorm(n_sim, logMPN_mean, logMPN_sd)
MPN_samp = 10^logMPN_samp
MPN_samp_halfgal = MPN_samp * 1900 #MPN per half gallon (1892.71 mL in half gallon)

#Temperature data
stages <- read.csv("temp_stages.csv", stringsAsFactors = F, comment.char = "#")

#Generate initial MPN for each half gallon from Poisson distribution
#Also sample AT for each half gallon
MPN_init<-vector()
allele <- vector()
temps <- vector()
for (i in 1:n_sim){
  MPN_init_samp <-rep(rpois(n_halfgal, MPN_samp_halfgal[i]), times = n_day)
  MPN_init<-c(MPN_init, MPN_init_samp)
  allele_samp <- rep(sample(freq_data, n_halfgal, replace = T), times = n_day)
  allele <- c(allele, allele_samp)
  #now calculate temp
  for (j in 1:nrow(stages)){
    stage_row <- stages[j, ]
    n_times <- stage_row$endTime - stage_row$beginTime + 1
    params <- as.numeric(unlist(strsplit(stage_row$parameters, " ")))
    temp_mean <- params[[1]]
    temp_sd <- params[[2]]
    temp_sample <- rep(rnorm(n_halfgal, temp_mean, temp_sd), times = n_times)
    temps <- c(temps, temp_sample)
  }
}
#add in temperature
data$temp <- temps

#Convert MPN_init from half-gallon to mLs
MPN_init_mL <- MPN_init / 1900
#remove 0's from the data and replace with detection limit
MPN_init_mL[MPN_init_mL == 0] <- 0.01;

#Now we add in those calculations to our original dataframe
data$logMPN_init <- log10(MPN_init_mL) #Add initial logMPN to data frame
data$AT<-allele #Add in AT data

##Now we will calculate the log10N for each row in the data frame
##Get the AT and day from the data frame, get growth parameters depending on the AT
# Simulation   ----
for (i in 1:(n_sim *n_halfgal * n_day)){
  #Find row in growth parameter data that corresponds to allele sample
  allele_index <- which(growth_import$rpoBAT == data$AT[i]) 
  
  #calculate the new growth parameters using the square root model and our
  #sampled temperature
  newT <- data$temp[i]
  newLag <- lagAtNewTemp(newT, growth_import$lag[allele_index])
  newMu <-  muAtNewTemp(newT, growth_import$mumax[allele_index])
  
  #Calculate the log10N count using our new growth parameters
  data$count[i] <- log10N_func(data$day[i], 
                               newLag, 
                               newMu,
                               data$logMPN_init[i],
                               growth_import$LOG10Nmax[allele_index])

}
