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



def get_summary_stats(for_boxplot:False, for_verschil:True):
    # Returns a dataframe with summary statistics of Leijgraaf stream
    compartments = list_stuwvak("Leijgraaf")
    if for_boxplot:
        dct_stats = {"Compartment":[i for i in compartments for _ in range(3)], "value":[], "type":[]}
        dct_i = {1:"mean", 2:"std", 3:"negative_values"}
    else:
        dct_stats = {"Stuwvak":compartments, "v_mean":[], "v_std":[], "v_negatives":[], "q_mean":[], "q_std":[], "q_negatives":[]}

    for comp in compartments:
        df = pd.read_csv(data_path + s + "feature_tables" + s + comp + "_feature_table.csv")
        if for_boxplot:
            if for_verschil:
                stats = df["VERSCHIL"].describe()
                col = "VERSCHIL"
            else:
                stats = df["Q"].describe()
                col = "Q"
            for i in range(1,4):
                if i == 3:
                    dct_stats["value"].append(df[df[col] <= 0].shape[0])
                else:
                    dct_stats["value"].append(stats[i])
                dct_stats["type"].append(dct_i[i])
        else:
            verschil_stats = df["VERSCHIL"].describe()
            q_stats = df["Q"].describe()
            dct_stats["v_mean"].append(verschil_stats["mean"])
            dct_stats["v_std"].append(verschil_stats["std"])
            dct_stats["v_negatives"].append(df[df["VERSCHIL"] <= 0].shape[0])
            dct_stats["q_mean"].append(q_stats["mean"])
            dct_stats["q_std"].append(q_stats["std"])
            dct_stats["q_negatives"].append(df[df["Q"] <= 0].shape[0])
    
    return pd.DataFrame(dct_stats)


def main():
    df = waterway_complete(waterway, path_to_stuw_order, path_to_ft_tables)
    df.to_csv(waterway + "_waterway.csv")


if __name__ == '__main__':
    main()
