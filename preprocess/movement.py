import pandas as pd

def stopped(df):
    """
    Keyword arguments:
    df -- Dataframe de emissões (Dataframe)

    Lê a fonte de emissões e retorna a condição em que o veículo está ou não andando.
    """

    #

    criteria_1 = df["NOx"] <= 250
    criteria_2 = df["NOx_max"] <= 300
    criteria_3 = df["NOx_dp"] <= 50
    criteria_4 = df["velocidad_kmh"] <=5       
   # criteria_5 = df["velocidad_kmh"] <= 100 #criteria_4 & criteria_3
    criteria = criteria_4 & criteria_3 & criteria_2 & criteria_1
    return criteria

def stopped_df(df):
    """
    Keyword arguments:
    df -- Dataframe de emissões (Dataframe)

    Lê a fonte de emissões e adiciona a coluna que indica se o veículo está ou não andando.
    """
    df["label_parado_nox"] = stopped(df)
    return df