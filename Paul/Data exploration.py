import pandas as pd
import numpy as np
import pyreadr

df_feature1 = pd.read_csv('../data/feature_tables/103BIB_103BIC_feature_table.csv')
print(df_feature1)
#

# df_stuw1 = pd.read_csv('../data/stuw_order.csv')
# # print(df_stuw1)
#
# df_rain1 = pd.read_csv('../data/rain_historic_timeseries/Download__5_201805312200_201806302200.csv')
#
# df_rain1 = df_rain1.drop(df_rain1.index[0])
# df_rain1 = df_rain1.reset_index()
# df_rain1 = df_rain1.rename(columns=df_rain1.iloc[0]).drop(0)
# df_rainpp = pd.DataFrame()
# df_rainpp[df_rain1.columns[:3]] = df_rain1[df_rain1.columns[:3]]
# df_rainpp = pd.concat([df_rainpp, df_rain1[df_rain1.columns[3:]].astype(float)], axis=1)

# print(df_rainpp.columns)



# result = pyreadr.read_r('../data/preprocessed/geometrie_peilbuizen.rds')
#
# print(result)\

# df_with_special_characters <- readRDS("../data/preprocessed/geometrie_peilbuizen.rds")
#
# write.csv(df_with_special_characters, "first.csv", row.names=FALSE)
# first <- read.csv("first.csv")
# print(first)