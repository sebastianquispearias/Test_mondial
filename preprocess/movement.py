import pandas as pd

def stopped(df):
    """
    Keyword arguments:
    df -- Dataframe de emissões (Dataframe)

    Lê a fonte de emissões e retorna a condição em que o veículo está ou não andando.
    """
    criteria_1 = df["NOx"] <= 250
    criteria_2 = df["NOx_max"] <= 300
    criteria_3 = df["NOx_dp"] <= 50
    criteria = criteria_1 & criteria_2 & criteria_3
    return criteria

def stopped_df(df):
    """
    Keyword arguments:
    df -- Dataframe de emissões (Dataframe)

    Lê a fonte de emissões e adiciona a coluna que indica se o veículo está ou não andando.
    """
    df["label_parado_nox"] = stopped(df)
    return df