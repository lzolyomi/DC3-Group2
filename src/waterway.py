import pandas as pd

# All waterways: Leijgraaf, Hertogswetering_, Raam, Strijpse Beek_, Osse Aanvoersloot, Peelse Loop_
# SIDENOTE: the last 3 waterways will give an error since the feature table of 1 or more compartments is not present

# ----Adjust the variables here
waterway = 'Leijgraaf'
path_to_stuw_order = "/Users/Gebruiker/OneDrive - TU Eindhoven/jaar3/DC3/DC3-Group2/data/stuw_order.csv"
path_to_ft_tables = "/Users/Gebruiker/OneDrive - TU Eindhoven/jaar3/DC3/DC3-Group2/data/feature_tables/"


def waterway_summary(waterway: str, path_to_stuw_order: str, path_to_ft_tables: str):
    """
        input:
        waterway: name of the waterway
        path_to_stuw_order: path to the stuw_order.csv on your device .../data/stuw_order.csv
        path_to_ft_tables: path to the feature tables on your device  .../feature_tables/

        output:
        gives all the weir compartments of the waterway together with the mean discharge per weir compartment
    """

    stuw_order = pd.read_csv(path_to_stuw_order)

    waterway_df = stuw_order.loc[stuw_order['WATERLOOP'] == waterway].iloc[::-1]  # select only those rows belonging to the waterway
    waterway_df.reset_index(inplace=True)
    waterway_df.drop(['index', 'ORDER'], axis=1)

    df = pd.DataFrame()
    for x in waterway_df.iloc[:, 3]:  # for each department, add it to the dataframe and addthe mean discharge per compartment for now

        vak = pd.read_csv(path_to_ft_tables + f"{x}_feature_table.csv")
        mean_weir = vak[['Q']].mean()
        df = df.append({'Weir compartment': x, 'Mean discharge': mean_weir[0]}, ignore_index=True)

    return df


def main():
    df_stream = waterway_summary(waterway, path_to_stuw_order, path_to_ft_tables)
    print(df_stream)


if __name__ == '__main__':
    main()
