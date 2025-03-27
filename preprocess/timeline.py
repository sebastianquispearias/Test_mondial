
from tqdm import tqdm
import pandas as pd
import numpy as np
from datetime import datetime, timezone
"""
Passo a passo para uso das funções:
- Importar os dados de emissões, vaigens e abastecimento
- Usar a função "add_data" para criar a coluna de data para os dados de abastecimento e emissões
    abastecimento = add_data(abastecimento)
    emissoes = add_data(emissoes)
- Usar a função "add_data_viagem"
    viagens_data = add_data_viagem(viagens)
- Usar a função "concatena_info" para concatenar as informações de todas as bases de dados
    timeline = concatena_info(viagens_data,emissoes,abastecimento)
"""

# Adiciona uma coluna com a informação de data (converte timestamp para data)
#  Deve ser usado apenas para os dados de abastecimento e emissões
"""
abastecimento = add_data(abastecimento)
emissoes = add_data(emissoes)
"""
def add_data(df):
        list_index = df.index
        df_copy = df.copy()

        for i in tqdm(range(len(list_index))):
                df_copy.loc[list_index[i],"data"] = datetime.fromtimestamp(df.loc[list_index[i],"timestamp"]/1000,timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')

        df_copy["data"] = pd.to_datetime(df_copy["data"],utc=True)
        df_copy["data"] = df_copy["data"].dt.tz_convert(None)

        return df_copy



# Cria uma coluna com informações de data apenas para os dados de viagem
"""
-Remove NaT
-A coluna de data é baseada nas informações do início e fim da viagem, bem como nas
informações das paradas de cada viagem
"""
def add_data_viagem(df):

    viagens = df.copy()
    viagens["actualStopStartDate"] = pd.to_datetime(viagens["actualStopStartDate"])
    viagens["actualStopEndDate"] = pd.to_datetime(viagens["actualStopEndDate"])
    viagens["actualTripStartDate"] = pd.to_datetime(viagens["actualTripStartDate"])
    viagens["actualTripEndDate"] = pd.to_datetime(viagens["actualTripEndDate"])

    viagens["actualStopStartDate"] = viagens["actualStopStartDate"].dt.tz_convert(None)
    viagens["actualStopEndDate"] = viagens["actualStopEndDate"].dt.tz_convert(None)
    viagens["actualTripStartDate"] = viagens["actualTripStartDate"].dt.tz_convert(None)
    viagens["actualTripEndDate"] = viagens["actualTripEndDate"].dt.tz_convert(None)

    # procurando por NaT
    df_check = np.isnat(viagens.loc[:, viagens.dtypes == 'datetime64[ns]'])

    viagens_copy = viagens.copy()

    index_drop = []
    for index in viagens_copy.index:
        if (viagens_copy.loc[index,"stopNumber"]>-1) & (df_check.loc[index,"actualStopEndDate"]==True | df_check.loc[index,"actualStopStartDate"]==True):
            index_drop.append(index)
    viagens_copy.drop(index_drop,inplace=True)

    new_viagens = pd.DataFrame(columns=viagens_copy.columns)
    new_viagens["data"] = 0
    datas = []
    for index in tqdm(list(viagens_copy.index)):
        if viagens_copy.loc[index,"stopNumber"]==-1:
            new_viagens = new_viagens.append(viagens_copy.loc[index,:], ignore_index = True)
            datas.append(new_viagens.loc[index,"actualTripStartDate"])
        elif viagens_copy.loc[index,"stopNumber"]==-2:
            new_viagens = new_viagens.append(viagens_copy.loc[index,:], ignore_index = True)
            datas.append(new_viagens.loc[index,"actualTripEndDate"])
        else:
            new_viagens = new_viagens.append(viagens_copy.loc[index,:], ignore_index = True)
            datas.append(new_viagens.loc[index,"actualStopStartDate"])

            new_viagens = new_viagens.append(viagens_copy.loc[index,:], ignore_index = True)
            datas.append(new_viagens.loc[index,"actualStopEndDate"])

    for index in tqdm(list(new_viagens.index)):
        if new_viagens.loc[index,"stopNumber"]>-1:
            if new_viagens.loc[index,"stopNumber"] == new_viagens.loc[index+1,"stopNumber"]:
                new_viagens.loc[index,"data"] = new_viagens.loc[index,"actualStopStartDate"]
                new_viagens.loc[index+1,"data"] = new_viagens.loc[index+1,"actualStopEndDate"]
        if new_viagens.loc[index,"stopNumber"]==-1:
            new_viagens.loc[index,"data"] = new_viagens.loc[index,"actualTripStartDate"]
        if new_viagens.loc[index,"stopNumber"]==-2:
            new_viagens.loc[index,"data"] = new_viagens.loc[index,"actualTripEndDate"]


    return new_viagens


# Agrega as informações de todas as bases de dados
def concatena_info(viagem,emissoes,abastecimento):
    new_viagens = viagem.copy()
    new_emissoes = emissoes.copy()
    new_abastecimento = abastecimento.copy()
    
    new_viagens['stop_id'] = np.arange(new_viagens.shape[0])
    new_emissoes['nox_id'] = np.arange(new_emissoes.shape[0])
    new_abastecimento['fuel_id'] = np.arange(new_abastecimento.shape[0])

    new_viagens.set_index('data',inplace=True)
    new_emissoes.set_index('data',inplace=True)
    new_abastecimento.set_index('data',inplace=True)

    ems_abst_viag = pd.concat([new_emissoes,new_abastecimento,new_viagens])
    ems_abst_viag = ems_abst_viag.sort_index(ascending=True)

    ems_abst_viag_copy = ems_abst_viag.copy()
    ems_abst_viag_copy = ems_abst_viag_copy.where(ems_abst_viag_copy.notnull(), None)


    return ems_abst_viag_copy

