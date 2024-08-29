import json
import requests
import pandas as pd
import time
import datetime
import tqdm
import os


def nox(token, df_path, start=-1, finish=-1):
    update_df(token, df_path, 'NOx_ecu', start, finish) 

def fuel(token, df_path, start=-1, finish=-1):
    new_fuel = update_df(token, df_path, 'wm_truck_ecu', start, finish)
    
# Consulta por veículo e apenas valores novos
def update_df(token, df_path, template_name, start=-1, finish=-1):
    """
    Keyword arguments:
    token -- autorização do http (Integer)
    template_name -- tipo de sensor (String)

    Dado um tipo de sensor, retorna todas as informações de todos os sensores + seu caminhão.
    Serve para consultar sensores de NOx e Abastecimento.
    Retorna um dataframe pandas contendo as informações.
    """
    id_to_fleet = _id_to_fleet(token)
    sensors_list = _sensors(token, template_name)
    metric_names = _sensor_metrics(token, template_name) 
    _metrics(token, sensors_list, metric_names, id_to_fleet, df_path, start, finish)

def vehicles(token, vehicle_df_path):
    """
    Keyword arguments:
    token -- autorização do http (Integer)

    Consulta os dados de todos os ativos.
    Retorna todas os caminhões em um dataframe pandas.
    """

    headers = _create_header(token)
    url = "https://iot-backend.sapienz.alis.solutions/registry/automation/monitored_object/supermercadomundial"
    response = requests.request("GET", url, headers=headers, data={})
    consulta = response.json()

    # Pega onde ficam as informações relevantes
    df_veiculos = []
    for truck in consulta["items"]:
        df_veiculos.append(truck['customData'])

    df = pd.DataFrame(df_veiculos)
    df.to_csv(vehicle_df_path, index=False)

def _create_header(token):
    """Serve somente para limpar o código considerando que o header é chamado muitas vezes"""
    return { 'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

def _can_convert_to_int(string):
    """
    Solução simples para a função lá em baixo que precisa saber qual é o fleet number 
    de um determinado caminhão. O dicionário existe, mas não há garantia de que o val
    or seja compátivel com algo inteiro.
    """
    try:
        int(string)
        return True
    except ValueError:
        return False

def _split_time(start, finish):
    """
    Keyword arguments:
    start -- começo da partição em milisegundos (Integer)
    finish -- final da partição, idealmente no momento atual(Integer)

    Quebra um range de datas em datas compatíveis com o sistema da Alis
    (UNIX timestamp * 1000) de tamanho < 1 ano.
    """

    lista_datas = []
    day = 86400000
    approximate_year = int(day*60)
    start = int(start)
    finish = int(finish)
    for i in range(start, finish, approximate_year):
        if i+approximate_year < finish: 
            lista_datas.append((i, i+approximate_year))
        else:
            lista_datas.append((i, finish))

    return lista_datas


# Helper que será usado posteriormente para dar chaves às métricas
def _id_to_fleet(token):
    """
    Keyword arguments:
    token -- autorização do http (Integer)

    Solicita todos os ativos da White Martins
    'Ativos' -> caminhões
    """

    headers = _create_header(token)
    url = "https://iot-backend.sapienz.alis.solutions/registry/automation/monitored_object/supermercadomundial" 
    response = requests.request("GET", url, headers=headers, data={})
    consulta = response.json()
    
    # Pega a relação nome -> numero frota
    id_to_fleet = {}
    for vehicle in consulta['items']:
        if 'fleet_number' in vehicle['customData']:
            fleet_number = vehicle['customData']['fleet_number']
            id_to_fleet[vehicle['compoundId']['identifier']] = fleet_number

    return id_to_fleet

def _sensor_metrics(token, template_name):
    """
    Keyword arguments:
    token -- autorização do http (Integer)
    template_name -- o template a ser consultado (String)
    
    Solicita as métricas de sensores que correspondem à um template_name,
    Ex, "wm_truck_ecu" e "wm_NOx_ecu"
    Retorna uma lista
    """

    headers = _create_header(token)
    url = "https://iot-backend.sapienz.alis.solutions/registry/automation/metric_source_type/supermercadomundial"
    response = requests.request("GET", url, headers=headers, data={})
    sensor_types = response.json()
    
    names = []
    for sensor_type in sensor_types['items']:
        id = sensor_type['compoundId']['identifier']
        if id == template_name:
            for metric in sensor_type['metrics']:
                name = metric['name']
                names.append(name)
    return names

def _sensors(token, template_name):
    """
    Keyword arguments:
    token -- autorização do http (Integer)
    template_name -- o template a ser consultado (String)
    
    Solicita os identificadores de sensores que correspondem à um template_name,
    Ex, "wm_truck_ecu" e "wm_NOx_ecu"
    Retorna uma lista
    """

    headers = _create_header(token)
    url = "https://iot-backend.sapienz.alis.solutions/registry/automation/metric_source/supermercadomundial"
    response = requests.request("GET", url, headers=headers, data={})
    consulta = response.json()

    lista_id_sensor = []
    for item in consulta["items"]:
        if "metricSourceTypeIdentifier" in item:
            if item["metricSourceTypeIdentifier"] == template_name:
                lista_id_sensor.append((item["compoundId"]["identifier"],item["monitoredObjectIdentifier"]))
    return lista_id_sensor


# Faz queries de uma métrica em específico
def _metric(token, metric, sensor, start, end):
    """
    Keyword arguments:
    token -- autorização do http (Integer)
    metric -- o nome do registro da série temporal (String)
    sensor -- o identificador do sensor (String)
    start -- unix timestamp da data inicial da request (Integer, UNIX Timestamp in milliseconds)

    Requisita uma série metric de um sensor de um timestamp start até o timestamp end
    Retorna uma lista que posteriormente será agragada à um índice temporal, na função _metrics(...)
    """

    headers = _create_header(token)
    url = "https://iot-backend.sapienz.alis.solutions/metric-series/supermercadomundial/" 
    payload = json.dumps({"id": sensor, "metricName": metric, "startTimestamp": start, "endTimestamp":  end})
    response = requests.request("POST", url=url, headers=headers, data=payload)
    time.sleep(0.5)
    try:
        series = [item for item in response.json()] 
        return series
    except:
        print('Não fez o decode')
        return None
    
# Faz queries de multiplas métricas de sensores
def _metrics(token, sensors_list, metric_names, id_to_fleet, df_path, start=-1, finish=-1):
    """
    Keyword arguments:
    token -- autorização do http (Integer)
    sensors_list -- lista de identificadores de sensores (List<String>)
    metric_names -- lista de diferentes valores a serem requisitados (List<String>)
    
    Faz requests de todos os sensores em todas as métricas e converte seus ids em fleet number (identificador padrão)
    Retorna um dataframe regular
    """

    column_names = ["vehicle_number", "vehicle_name", "timestamp"] + metric_names

    # Se existe, Recupera
    # Senão, Cria
    df_exists = os.path.exists(df_path)
    if not df_exists: 
        old_df = pd.DataFrame(columns=column_names)
    else:
        old_df = pd.read_csv(df_path)

    # Comportamentos padrões de tempo
    if start < 0 and finish < 0:
        earliest = "01/01/2024"
        finish = int(time.time()*1000)
        start = int(time.mktime(datetime.datetime.strptime(earliest, "%d/%m/%Y").timetuple())*1000)

    # Para cada sensor
    # Se o nome é um veículo válido
    # Faz as requests
    for sensor_name, vehicle_name in sensors_list:
        if vehicle_name in id_to_fleet:

            # TRATAMENTO IMPOSSÍVEL NA supermercadomundial
            # if _can_convert_to_int(id_to_fleet[vehicle_name]):
                # print(start, finish)

            # Pega o último registro 
            # As requests começam nele
            if vehicle_name in old_df['vehicle_name'].unique():
                selector = old_df['vehicle_name'] == vehicle_name
                start = old_df[selector]['timestamp'].max()
            # Consulta todas as métricas
            # Encaixa nos dados de veículos com o tempo como índice
            # Adiciona no dataframe original
            time_tuples = _split_time(start, finish)
            pbar = tqdm.tqdm(time_tuples, desc=f'Loading {vehicle_name}')
            for time_interval in pbar:
                vehicle_df = pd.DataFrame(columns=column_names)
                start_date, end_date = time_interval
                s = datetime.date.fromtimestamp(start/1000)
                e = datetime.date.fromtimestamp(end_date/1000)
                pbar.set_description(f'Loading {vehicle_name} - [{s}, {e}]')
                for metric_name in metric_names:
                    serie = _metric(
                        token, 
                        metric_name, 
                        sensor_name, 
                        start_date, 
                        end_date
                    )
                    if len(serie) > 0:
                        metric_df = pd.DataFrame(serie)
                        metric_df = metric_df.rename(columns={'value': metric_name})
                        metric_df = metric_df.set_index('timestamp')
                        vehicle_df[metric_name] = metric_df[metric_name]
                        vehicle_df['timestamp'] = vehicle_df.index

                vehicle_df['vehicle_name'] = vehicle_name
                vehicle_df['vehicle_number'] = id_to_fleet[vehicle_name]
                old_df = pd.concat([old_df, vehicle_df], ignore_index=True)
                old_df.to_csv(df_path, index=False)