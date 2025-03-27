import pandas as pd

'''
Este módulo possuí funções que lêem um ou dois Dataframes e aplica uma função de filtro.
Este filtro retorna o Dataframe sem o dado quando arg_return é 0.
Se arg_return é 1, retorna somente o que deveria ter sido excluído.
Se arg_return é 2, retorna a tupla (valido, invalido).
'''

# Verifica se a quantidade de litros abastecido por um veículo viola a capacidade do tanque
def filter_liter_supply(dados_abastecimento, dados_veiculos, arg_return):
    dados_veiculos = dados_veiculos.rename(columns={"fleet_number": "vehicle_number"})
    dados = dados_abastecimento.merge(dados_veiculos, on="vehicle_number")
    
    def tank_cut(data, vehicle_type, tank_capacity):
        vehicle_type = data[data["vehicle_type"] == vehicle_type]
        criteria = vehicle_type["liter_supply"] <= tank_capacity
        invalid = vehicle_type[~criteria]
        valid = vehicle_type[criteria]
        return valid, invalid

    horse_valid,  horse_invalid = tank_cut(dados, "horseMechanics", 700)
    medium_valid, medium_invalid = tank_cut(dados, "mediumTruck", 275)
    small_valid,  small_invalid = tank_cut(dados, "smallTruck", 275)
    notype_valid, notype_invalid = tank_cut(dados, "notype", 275)

    valid = [
        horse_valid, 
        medium_valid, 
        small_valid, 
        notype_valid
    ]
    valid = pd.concat(valid)[dados_abastecimento.columns]
    # valid = valid[dados_abastecimento.columns]
    
    invalid = [
        horse_invalid,
        medium_invalid, 
        small_invalid, 
        notype_invalid
    ]
    invalid = pd.concat(invalid)[dados_abastecimento.columns]
    # invalid = invalid[dados_abastecimento.columns]

    if arg_return == 0:
        return valid
    elif arg_return == 1:
        return invalid
    elif arg_return == 2:
        return valid, invalid


# Verifica o consumo de combustível (igual ou menor que zero, acima de dez litros)
def filter_consumption(dados_abastecimento, arg_return):
    lower = dados_abastecimento["consumption"] > 0 
    upper = dados_abastecimento["consumption"] < 15
    consumption_criteria = lower & upper
    valid = dados_abastecimento[consumption_criteria]
    invalid = dados_abastecimento[~consumption_criteria]
    if arg_return == 0:
        return valid
    elif arg_return == 1:
        return invalid
    elif arg_return == 2:
        return valid, invalid


# Verifica a quantidade de km rodados (igual ou menor que zero, acima de 2000 km)
def filter_km(dados_abastecimento,arg_return):
    lower = dados_abastecimento["km_driven"] > 0
    upper = dados_abastecimento["km_driven"] < 2000
    consumption_criteria = lower & upper
    valid = dados_abastecimento[consumption_criteria]
    invalid = dados_abastecimento[~consumption_criteria]
    if arg_return == 0:
        return valid
    elif arg_return == 1:
        return invalid
    elif arg_return == 2:
        return valid, invalid


# Verifica se o valor do hodômetro é menor ou igual a zero
# Se a leitura seguinte é igual ou inferior à anterior
def filter_odometer(dados_abastecimento, arg_return):
    valid = []
    invalid = []
    
    for _, data in dados_abastecimento.groupby('vehicle_number'):
        data = data.sort_values(by='timestamp')
        diff = data['odometer'].diff()
        criteria = diff >= 0
        valid.append(data[criteria]) 
        invalid.append(data[~criteria])
    
    valid = pd.concat(valid)
    invalid = pd.concat(invalid)

    if arg_return == 0:
        return valid
    if arg_return == 1:
        return invalid
    if arg_return == 2:
        return valid, invalid


# HELPER, considerando que essa regra se repete demais em várias colunas
# Ex: nox, min, max, std
# Existe uma semelhante com O2, mas o cast é diferente
# Verifica se é maior que zero e é conversível em inteiro
def filter_leq(dados_nox, key, limit=0):
    dados_nox = dados_nox.fillna(limit - 1)
    criteria_1 = dados_nox[key]!=dados_nox[key].astype(int)
    criteria_2 = dados_nox[key].astype(int) >= limit
    criteria = criteria_1 | criteria_2
    return criteria

# Não pode haver data inferior a 28 de fevereiro de 2022
def filter_data_inicial(dados_nox, arg_return, time_cut=1646017200):
    criteria = dados_nox['timestamp'] >= time_cut*1000
    valid = dados_nox[criteria]
    invalid = dados_nox[~criteria]
    
    if arg_return == 0:
        return valid
    if arg_return == 1:
        return invalid
    if arg_return == 2:
        return valid, invalid

# Valor numérico inteiro
# Não pode ser menor ou igual a zero
def filter_numero(dados_nox, arg_return):
    criteria = filter_leq(dados_nox, 'vehicle_number', 0)
    
    valid = dados_nox[criteria]
    invalid = dados_nox[~criteria]
    
    if arg_return == 0:
        return valid
    if arg_return == 1:
        return invalid
    if arg_return == 2:
        return valid, invalid

# NOx não pode estar abaixo de zero
def filter_nox_avg(dados_nox, arg_return):
    criteria = filter_leq(dados_nox, 'NOx', 0)
    valid = dados_nox[criteria]
    invalid = dados_nox[~criteria]
    
    if arg_return == 0:
        return valid
    if arg_return == 1:
        return invalid
    if arg_return == 2:
        return valid, invalid

# NOx Min não pode estar abaixo de zero
def filter_nox_min(dados_nox, arg_return):
    criteria = filter_leq(dados_nox, 'NOx_min', 0)
    valid = dados_nox[criteria]
    invalid = dados_nox[~criteria]
    
    if arg_return == 0:
        return valid
    if arg_return == 1:
        return invalid
    if arg_return == 2:
        return valid, invalid

# NOx Max não pode estar abaixo de zero
def filter_nox_max(dados_nox, arg_return):
    criteria = filter_leq(dados_nox, 'NOx_max', 0)
    valid = dados_nox[criteria]
    invalid = dados_nox[~criteria]
    
    if arg_return == 0:
        return valid
    if arg_return == 1:
        return invalid
    if arg_return == 2:
        return valid, invalid

# NOx Std não pode estar abaixo de zero
def filter_nox_std(dados_nox, arg_return):
    criteria = filter_leq(dados_nox, 'NOx_dp', 0)
    valid = dados_nox[criteria]
    invalid = dados_nox[~criteria]
    
    if arg_return == 0:
        return valid
    if arg_return == 1:
        return invalid
    if arg_return == 2:
        return valid, invalid

# O2 não pode estar abaixo de zero
def filter_o2(dados_nox, arg_return):
    key = 'O2'
    criteria_1 = dados_nox[key]!=dados_nox[key].astype(float)
    criteria_2 = dados_nox[key].astype(float) > 0
    criteria = criteria_1 | criteria_2
    valid = dados_nox[criteria]
    invalid = dados_nox[~criteria]
    
    if arg_return == 0:
        return valid
    if arg_return == 1:
        return invalid
    if arg_return == 2:
        return valid, invalid

# NOx não pode estar abaixo de 100 se o O2 está acima de 19.6%
# Significa que o veículo não foi ligado, mas o sensor ligou
def filter_desligado(dados_nox, arg_return):
    criteria_1 = dados_nox['O2'] > 19.6
    criteria_2 = dados_nox['NOx'] < 100
    criteria = criteria_1 & criteria_2

    valid = dados_nox[~criteria]
    invalid = dados_nox[criteria]
    if arg_return == 0:
        return valid
    if arg_return == 1:
        return invalid
    if arg_return == 2:
        return valid, invalid

# Significa que houve falha no sensor e os dados estão errados
def filter_nox_duplicates(dados_nox, arg_return):
    criteria = dados_nox.duplicated(
        subset=[
            'NOx', 
            'NOx_min', 
            'NOx_max', 
            'NOx_dp'
        ], 
        keep='first'
    )
    
    valid = dados_nox[~criteria]
    invalid = dados_nox[criteria]
    if arg_return == 0:
        return valid
    if arg_return == 1:
        return invalid
    if arg_return == 2:
        return valid, invalid


# Significa que houve falha no GPS, mas não precisa descartar
"""
def filter_coordinate_duplicates(dados_nox, arg_return):
    criteria = dados_nox.duplicated(subset=['position'], keep='first')
    valid = dados_nox[~criteria]
    invalid = dados_nox[criteria]
    if arg_return == 0:
        return valid
    if arg_return == 1:
        return invalid
    if arg_return == 2:
        return valid, invalid
"""
# Significa que houve falha no GPS, mas não precisa descartar
def filter_coordinate_in_brazil(dados_nox, arg_return):
    # Brazil bb
    x_max = -28.850  
    x_min = -73.817   
    y_max = 16.800
    y_min = -33.733  

    
    dados_nox[['x', 'y']] = dados_nox['position'].str.split(" ", expand=True)
    x = dados_nox['x'].str.extract('(\d+)', expand=False)
    x = x.astype(float)
    y = dados_nox['y'].str.extract('(\d+)', expand=False)
    y = y.astype(float)

    y_valid = (y > y_min) | (y < y_max)
    x_valid = (x > x_min) | (x < x_max)
    criteria = x_valid & y_valid

    dados_nox = dados_nox.drop(['x', 'y'], axis='columns')
    valid = dados_nox[criteria]
    invalid = dados_nox[~criteria]
    if arg_return == 0:
        return valid
    if arg_return == 1:
        return invalid
    if arg_return == 2:
        return valid, invalid