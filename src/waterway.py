import pandas as pd
from file_struct import locate_data_
import platform

# All waterways: Leijgraaf, Hertogswetering_, Raam, Strijpse Beek_, Osse Aanvoersloot, Peelse Loop_
# SIDENOTE: the last 3 waterways will give an error since the feature table of 1 or more compartments is not present

# ----Adjust the waterway here
waterway = 'Leijgraaf'

data_path = locate_data_()

if platform.system() == 'Windows':  # checks for the system to get the paths right
    s = '''\\'''
else:
    s = '''/'''

path_to_stuw_order = str(data_path) + s + "stuw_order.csv"
path_to_ft_tables = str(data_path) +  s + "feature_tables" + s


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

    df = pd.DataFrame()
    for dep in waterway_df.iloc[:, 2]:  # for each department, add it to the dataframe and add the mean discharge per compartment for now

        compartment = pd.read_csv(path_to_ft_tables + f"{dep}_feature_table.csv")
        mean_weir = compartment[['Q']].mean()
        df = df.append({'Weir compartment': dep, 'Mean discharge': mean_weir[0]}, ignore_index=True)

    return df


def waterway_complete(waterway: str, path_to_stuw_order: str, path_to_ft_tables: str):
    stuw_order = pd.read_csv(path_to_stuw_order)

    waterway_df = stuw_order.loc[stuw_order["WATERLOOP"] == waterway].iloc[::-1]  # inverting dataframe

    df_list = []
    for dep in waterway_df.iloc[:, 2]:  # dep is name of weir compartment
        compartment = pd.read_csv(path_to_ft_tables + f"{dep}_feature_table.csv")  # whole feature table
        df_list.append(pd.DataFrame({"Time": compartment["TIME"], "Weir compartment": compartment["STUWVAK"], "Discharge(Q)": compartment["Q"], "Diff(Verschil)": compartment["VERSCHIL"]}))
    df = pd.concat(df_list)
    df["Time"] = pd.to_datetime(df["Time"])
    return df


def list_stuwvak(stream: str):
    """
    Returns a list with all the stuwvak IDs of selected stream"""
    df_summary = waterway_summary(stream, path_to_stuw_order, path_to_ft_tables)
    return list(df_summary["Weir compartment"])



def main():
    df = waterway_complete(waterway, path_to_stuw_order, path_to_ft_tables)
    df.to_csv(waterway + "_waterway.csv")


if __name__ == '__main__':
    main()
