#' extrapolate_begroeiing
#' Voorspellen van de begroeiing voor de aankomende 21 dagen, op basis van een lineair model. 
#' 
#' @param preds data nodig voor extrapolatie
#' @param timesteps tijdstappen, default = 7
#' @param gem_temp gemiddelde temperatuur de afgelopen tijd default = 22
#'
#' @return dataframe met extrapoleerde data voor in plotly
#' @export
extrapolate_begroeiing <- function(preds, timesteps = 7, gem_temp = 22) {
  if (nrow(preds) <= timesteps) {
    return()
  }
  
  # Ophalen data van de laatste 7 dagen
  last_data <- preds %>%
    tail(timesteps) %>%
    mutate(ID = 1:timesteps)
  
  # Minstens twee waarden
  if (length(which(!is.na(last_data$BEGROEIING))) < 2) {
    return()
  }
  
  ## Laatste datum opzoeken en er 21 dagen bijop tellen
  new_dates <- seq(last(last_data$TIME) + days(1), last(last_data$TIME) + days(21), 1)
  
  ## Op basis van de laatste 7 dagen via een lineair model model trainen
  extrapolate_model <- lm(BEGROEIING ~ ID, data = last_data)
  if (extrapolate_model$coefficients["ID"] < 0) {
    return() # Model voorspeld afname van begroeiing...
  }
  
  ## 21 dagen begroeiing voorspellen op basis van het estrapolatie_model
  new_vals <- predict(extrapolate_model, data.frame(ID = seq(timesteps + 1, timesteps + 21, 1)))
  
  # Niks teruggeven als de voorspelde begroeiing 0 blijft..
  if (all(new_vals == 0)) {
    return()
  }
  
  # Met warm weer: groei +20%
  # Koud weer: groei -20%
  if (!is.na(gem_temp) & gem_temp > 25) {
    new_vals <- new_vals * 1.2 ## TODO: Check Wat is de bron van factor 1.2?
  } else if (!is.na(gem_temp) & gem_temp < 20) {
    new_vals <- new_vals * 0.8 ## TODO: Check Wat is de bron van factor 0.8>
  }
  
  tibble(TIME = new_dates, PREDS = pmax(new_vals, 0)) %>%
    return()
}