#' Bereken de risico_categorie, gebaseerd op begroeiing
# Calculate risk category based on vegetation
#'
#' @param stuwvak (name of the weir compartment), naam van het stuwvak
#' @param risk_date (Date of the risk assessment), Datum van risico-inschatting
#'
#' @return Risk category of the growth in 25, 50, and 75% quantiles, Risico-categorie van de begroeiing en 25, 50 en 75% quantiles
#' @export
calc_begroeiing_risk <- function(stuwvak, risk_date, feature_table_path = "data/feature_tables/", model_path = "output/models/") {
  stuwvak_data <- get_feature_table(stuwvak, feature_table_path)
  current_year <- year(risk_date)

  if (!file.exists(sprintf("%s%s_%i.rds", model_path, stuwvak, current_year))) {
    return(NA)
  }
  model <- read_rds(sprintf("%s%s_%i.rds", model_path, stuwvak, current_year))

  huidig_begroeiing <- stuwvak_data %>%
    slice(n()) %>%
    select(VERSCHIL, Q)

  # Winter is coming
  if (month(risk_date) <= 2 | month(risk_date) >= 10) { # summer from march until september,  zomerperiode van maart tot en met september
    huidig_begroeiing <- NA_integer_
  } else if (huidig_begroeiing$Q <= 0) {
    warning("No debietdata for ", stuwvak, " on date ", risk_date)
    huidig_begroeiing <- NA_integer_
  } else if (length(huidig_begroeiing) == 0) {
    warning("No data for ", stuwvak, " on date ", risk_date)
    huidig_begroeiing <- NA_integer_
  } else {
    huidig_pred <- predict(model, select(huidig_begroeiing, Q)) %>% pmax(0)
    huidig_begroeiing <- pmax(0, huidig_begroeiing$VERSCHIL - huidig_pred)
  }

  min_year <- current_year - 3
  total_begroeiing <- c()
  for (i in min_year:current_year) {
    if (!file.exists(sprintf("%s%s_%i.rds", model_path, stuwvak, i))) {
      next
    }
    model_year <- read_rds(sprintf("%s%s_%i.rds", model_path, stuwvak, i))
    data_year <- filter(stuwvak_data, YEAR == i & MAAND > 2 & MAAND < 10) # summer from march until september, zomerperiode van maart tot en met september

    pred_year <- predict(model_year, select(data_year, Q)) %>% pmax(0)
    begroeiing_year <- pmax(0, data_year$VERSCHIL - pred_year)

    total_begroeiing <- c(total_begroeiing, begroeiing_year)
  }

  all_begroeiing <- quantile(total_begroeiing, na.rm = TRUE)

  risk_cat <- if_else(huidig_begroeiing > all_begroeiing[4], 4,
    if_else(huidig_begroeiing > all_begroeiing[3], 3,
      if_else(huidig_begroeiing > all_begroeiing[2], 2, 1)
    )
  )
  return(c(RISK = risk_cat, all_begroeiing[2], all_begroeiing[3], all_begroeiing[4]))
}

#' Bereken aantal punten voor neerslagtekort
# Calculate total points for the precipitation deficit
#'
#' @param neerslag_tekort percentage neerslagtekort berekent als
#' `(waarde - mediaan) / abs(mediaan) * 100`
# percentage precipitation deficit calculated as (value - median / {abs(median) *100})
#'
#' @return number of discharge and supply points, het aantal afvoer en aanvoerpunten
#' @export
neerslagtekort_risico <- function(neerslag_tekort) {
  afvoer_points <- if_else(neerslag_tekort <= 10 & neerslag_tekort >= -10, 1,
    if_else(neerslag_tekort < -10, 2,
      0
    )
  )
  aanvoer_points <- if_else(neerslag_tekort <= 10 & neerslag_tekort >= -10, 1,
    if_else(neerslag_tekort > 10, 2,
      0
    )
  )

  return(c(afvoer_points, aanvoer_points))
}

#' Bereken aantal punten voor grondwater
#  Calculate number of points for groundwater
#'
#' @param grondwater groundwater classification, grondwaterklasse (bijv. Droog)
#'
#' @return number of discharge and supply points, het aantal afvoer en aanvoerpunten
#' @export
grondwater_risico <- function(grondwater) {
  afvoer_points <- if_else(grondwater == "Normaal", 1,
    if_else(grondwater %in% c("Nat", "Erg nat"), 2,
      0
    )
  )

  aanvoer_points <- if_else(grondwater == "Normaal", 1,
    if_else(grondwater %in% c("Droog", "Erg droog"), 2,
      0
    )
  )

  return(c(afvoer_points, aanvoer_points))
}

#' Bereken het aantal punten voor neerslag
#' Calculate number of points for the precipitation
#' @param neerslag_verwachting dataframe met de verwachting
#' voor de komende 10 dagen
# Dataframe with expectation for the coming 10 days
#'
#' @return het aantal afvoer en aanvoerpunten
# Number of discharge and supply points
#' @export
neerslag_risico <- function(neerslag_verwachting) {
  natte_dagen <- neerslag_verwachting %>%
    filter(perc_nat >= 10) %>%
    pull(datum) %>%
    unique()
  erg_natte_dagen <- neerslag_verwachting %>%
    filter(perc_erg_nat >= 10) %>%
    pull(datum) %>%
    unique()

  # Opeenvolgende natte dagen
  #Consecutive wet days
  if (length(natte_dagen) > 1) {
    nat_counter <- 1
    for (i in 2:length(natte_dagen)) {
      if (natte_dagen[i] - natte_dagen[i - 1] == 1) {
        nat_counter <- nat_counter + 1
      } else {
        nat_counter <- 1
      }
    }
  } else {
    nat_counter <- 0
  }

  # Opeenvolgende erg natte dagen
  #Consecutive very wet days
  if (length(erg_natte_dagen) > 1) {
    erg_nat_counter <- 1
    for (i in 2:length(erg_natte_dagen)) {
      if (erg_natte_dagen[i] - erg_natte_dagen[i - 1] == 1) {
        erg_nat_counter <- erg_nat_counter + 1
      } else {
        erg_nat_counter <- 1
      }
    }
  } else {
    erg_nat_counter <- 0
  }

  afvoer_points <- if_else(nat_counter > 1 | length(erg_natte_dagen) > 0, 1,
    if_else(erg_nat_counter > 1, 2,
      0
    )
  )

  cum_gem <- neerslag_verwachting %>%
    summarise(cum_gem = sum(gemiddelde, na.rm = TRUE)) %>%
    pull(cum_gem)
  aanvoer_points <- if_else(cum_gem >= 30 & cum_gem <= 100, 1,
    if_else(cum_gem < 30, 2,
      0
    )
  )

  return(c(afvoer_points, aanvoer_points))
}

#' Bereken het aantal punten voor temperatuur
#Calculate the number of points for temperature
#'
#' @param temp_verwachting dataframe met de verwachting
#' voor de komende 10 dagen
#Dataframe with the expectation for the coming 10 days
#'
#' @return het aantal afvoer en aanvoerpunten (afvoer is altijd 0)
# The number of discharge and supply points (discharge is always 0)
#' @export
temp_risico <- function(temp_verwachting) {
  temp_verwachting <-
    filter(temp_verwachting, variable == "Tgem_verwachting") %>%
    filter(value >= 25) %>%
    nrow()

  aanvoer_points <- if_else(temp_verwachting > 5, 2,
    if_else(temp_verwachting > 3, 1,
      0
    )
  )

  return(c(0, aanvoer_points))
}

#' Bereken het aantal punten voor bewolking
# Calculate the nuber of points for the cloud cover
#'
#' @param bewolking_verwachting dataframe met de verwachting
#' voor de komende 10 dagen
#Dataframe with the expectation for the coming 10 days
#'
#' @return het aantal afvoer en aanvoerpunten (afvoer is altijd 0)
#The number of discharge and supply points, discharge is always 0
#' @export
bewolking_risico <- function(bewolking_verwachting) {
  dagen_minder_30 <- bewolking_verwachting %>%
    filter(gem_value <= 30) %>%
    nrow()

  average_bewolking <- mean(bewolking_verwachting$gem_value)
  aanvoer_points <- if_else(dagen_minder_30 >= 5, 2,
    if_else(average_bewolking >= 40 & average_bewolking <= 60, 1,
      0
    )
  )

  return(c(0, aanvoer_points))
}

#' Bereken het aan/afvoer risico 
#Calculate supply and discharge risk
#This is not based on date, when for example the precipitation deficit is missing from 16-2-2021, the risk points for the precipitation deficit on 25-2-2021 is then based on the data from 16-2-2021
#' Dit is niet op basis van datums. Ofwel wanneer bijvoorbeeld neerslagtekort ontbreekt vanaf 16-2-2021, de risicopunten voor neerslagtekort op 25-2-2021 is dan gebaseerd op de data van 16-2-2021
#' @param stuwvak Stuwvak_naam
#Weir name
#'
#' @return het aan- en afvoerrisico in punten
#The supply and discharge risks in points
#' @export
calc_risk <- function(stuwvak, waterloop_naam,
                      grondwater_path = "data/preprocessed/grondwater.rds",
                      neerslag_tekort_path = "data/preprocessed/neerslag_tekort_maaibos.rds",
                      neerslag_path = "data/preprocessed/neerslagverwachting.rds",
                      temperatuur_path = "data/preprocessed/temperatuur.rds",
                      bewolking_path = "data/preprocessed/bewolkingsgraad.rds",
                      waterlopen_path = "data/preprocessed/waterlopen.rds",
                      riool_overstort_path = "data/shapes/riooloverstort/riooloverstort.shp") {
  aanvoer_points <- 0
  afvoer_points <- 0
  # Bereken risico aan/afvoer
  
  waterloop_naam <- stringr::str_remove(waterloop_naam, "_")

  # Grondwater
  # Groundwater
  grondwater <- read_rds(grondwater_path) %>%
    filter(!is.na(Klasse), Waterloop == waterloop_naam) %>%
    slice(n()) %>%
    pull(Klasse)
  
  # print(sprintf("grondwaterklasse %s: %s", waterloop_naam, grondwater))
  #print( groundwater classification, waterway name, groundwater variable)

  grondwater_punten <- grondwater_risico(grondwater)
  afvoer_points <- afvoer_points + grondwater_punten[1]
  # print(sprintf("afvoerpunten %s: %s ", waterloop_naam, afvoer_points))
  #print(discharge points, waterway name, discharge points variable)
  aanvoer_points <- aanvoer_points + grondwater_punten[2]
  # print(sprintf("aanvoerpunten %s: %s ", waterloop_naam, aanvoer_points))
  # print( supply points, waterway name, supply point variable)

  # Neerslagtekort
  #Precipitation deficit
  neerslag_tekort <- read_rds(neerslag_tekort_path) %>%
    filter(!is.na(huidig_jaar)) %>%
    slice(n()) %>%
    mutate(PERC = (huidig_jaar - mediaan) / abs(mediaan) * 100) %>%
    pull(PERC)

  neerslagtekort_punten <- neerslagtekort_risico(neerslag_tekort)
  afvoer_points <- afvoer_points + neerslagtekort_punten[1]
  aanvoer_points <- aanvoer_points + neerslagtekort_punten[2]

  # Neerslagverwachting
  #Expected precipitation deficit
  neerslag_verwachting <- read_rds(neerslag_path) %>%
    mutate(datum = as.Date(DateTime))

  neerslag_punten <- neerslag_risico(neerslag_verwachting)
  afvoer_points <- afvoer_points + neerslag_punten[1]
  aanvoer_points <- aanvoer_points + neerslag_punten[2]

  # Temperatuurverwachting
  # Expected temperature
  temp_verwachting <- read_rds(temperatuur_path)

  temp_punten <- temp_risico(temp_verwachting)
  afvoer_points <- afvoer_points + temp_punten[1]
  aanvoer_points <- aanvoer_points + temp_punten[2]

  # Bewolkingverwachting
  # Expected cloud cover
  bewolking_verwachting <- read_rds(bewolking_path) %>%
    group_by(date) %>%
    summarise(gem_value = unique(gem_value))

  bewolking_punten <- bewolking_risico(bewolking_verwachting)
  afvoer_points <- afvoer_points + bewolking_punten[1]
  aanvoer_points <- aanvoer_points + bewolking_punten[2]

  # Overstort aanwezig
  # Overflow events
  shape_stuwvak <- read_rds(waterlopen_path) %>%
    filter(STUWVAK == stuwvak) %>%
    st_transform(28992)

  riool_overstort <- st_read(riool_overstort_path, crs = 28992)
  min(st_distance(shape_stuwvak, riool_overstort))
  afvoer_points <- if_else(as.double(min(st_distance(shape_stuwvak, riool_overstort))) <= 500,
    afvoer_points + 2, afvoer_points
  )

  return(c("AANVOER" = aanvoer_points, "AFVOER" = afvoer_points))
}
