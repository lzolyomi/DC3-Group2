#' extrapolate_begroeiing
#' Voorspellen van de begroeiing voor de aankomende 21 dagen, op basis van een lineair model. 
#' 
#' @param preds (data needed for extrapolation) data nodig voor extrapolatie
#' @param timesteps (time intervals, default 7) tijdstappen, default = 7
#' @param gem_temp (average temperature of the last time interval, defined above) gemiddelde temperatuur de afgelopen tijd default = 22
#'
#' @return (dataframe with extrapolated data for plotly) dataframe met extrapoleerde data voor in plotly
#' @export
extrapolate_begroeiing <- function(preds, timesteps = 7, gem_temp = 22) {
  if (nrow(preds) <= timesteps) {
    return()
  }
  
  # Ophalen data van de laatste 7 dagen
  # Pickup the data from the last 7 days
  last_data <- preds %>%
    tail(timesteps) %>%
    mutate(ID = 1:timesteps)
  
  # Minstens twee waarden
  # At minimum two growth values
  if (length(which(!is.na(last_data$BEGROEIING))) < 2) {
    return()
  }
  
  ## Laatste datum opzoeken en er 21 dagen bijop tellen
  ## Calculate 21 day forecast period
  new_dates <- seq(last(last_data$TIME) + days(1), last(last_data$TIME) + days(21), 1)
  
  ## Op basis van de laatste 7 dagen via een lineair model model trainen
  # Based on the last 7 days, train a linear model
  extrapolate_model <- lm(BEGROEIING ~ ID, data = last_data)
  if (extrapolate_model$coefficients["ID"] < 0) {
    return() # Model voorspeld afname van begroeiing...
  }          # Predicted vegetation decline by the model
  
  ## 21 dagen begroeiing voorspellen op basis van het estrapolatie_model
  # 21 day vegetation forecast from the extrapolated model
  new_vals <- predict(extrapolate_model, data.frame(ID = seq(timesteps + 1, timesteps + 21, 1)))
  
  # Niks teruggeven als de voorspelde begroeiing 0 blijft..
  # Return nothing if the vegetation forecast is 0
  if (all(new_vals == 0)) {
    return()
  }
  
  # Met warm weer: groei +20%
  # With warm weather increase the growth 20%

  # Koud weer: groei -20%
  # With cold weather decrease growth 20%
  if (!is.na(gem_temp) & gem_temp > 25) {
    new_vals <- new_vals * 1.2 ## TODO: Check Wat is de bron van factor 1.2?
                                #Check what the source of 1.2 value is
  } else if (!is.na(gem_temp) & gem_temp < 20) {
    new_vals <- new_vals * 0.8 ## TODO: Check Wat is de bron van factor 0.8>
  }                            #Check what the source of value 0.8 is
  
  tibble(TIME = new_dates, PREDS = pmax(new_vals, 0)) %>%
    return()
}