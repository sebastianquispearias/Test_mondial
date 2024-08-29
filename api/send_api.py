import requests
import json
import time
import pandas as pd

# Dada uma chave compatível com um dado que existe em nossos registros,
# Retorna a fonte do dado como um Dataframe 
# Retorna o nome utilizado para registro desse dado na plataforma da Alis
def retrieve_metric(path, filter="anomaly_consumption"):
    
    if filter=="anomaly_consumption":
        source = pd.read_csv(path+"anomalias/abastecimentos.csv")  
        source = source[source[filter] == 1]  
        local_name = "consumption"
        alis_name = "Ensemble Consumo"
    
    elif filter=="anomaly_liter_supply":
        source = pd.read_csv(path+"anomalias/abastecimentos.csv")
        source = source[source[filter] == 1]
        local_name = "liter_supply"
        alis_name = "Ensemble Litros"

    elif filter == "anomaly_km_driven":
        source = pd.read_csv(path+"anomalias/abastecimentos.csv")
        source = source[source[filter] == 1]
        local_name = "km_driven"
        alis_name = "Ensemble Km"

    elif filter=="anomaly_nox":
        source = pd.read_csv(path+"anomalias/nox.csv")
        source = source[source[filter] == 1]
        local_name = "NOx"
        alis_name = "Ensemble NOx"

    elif filter =="anomaly_o2":
        source = pd.read_csv(path+"anomalias/nox.csv")
        source = source[source[filter] == 1]
        local_name = "O2"
        alis_name = "Ensemble O2"

    elif filter =="label_parado_nox":
        source = pd.read_csv(path+"parado/nox.csv")
        local_name = "label_parado_nox"
        alis_name = "parado"

    source = source[[local_name, 'timestamp', 'vehicle_number']]
    source = source.rename(columns={local_name:alis_name})
    return source, alis_name

# Helper para verificar dados de hoje em dia até 6 meses atrás de um sensor em particular
def retrieve_six_months_ago(sensor, metric, auth, ambiente="DEV"):    
    url = "https://iot-backend.sapienz.alis.solutions/metric-series/supermercadomundial/"

    month = 2629800000
    current_time = time.time()*1000
    querry_begin = current_time - month*11

    payload = json.dumps({
        "id": sensor,
        "metricName": metric,
        "startTimestamp": int(querry_begin),
        "endTimestamp":  int(current_time)
    })
    print(payload)
    response = requests.request("POST", url, headers=auth, data=payload)
    return response.text

# Estrutura nomes de sensores
# Verifica quais placas e convenções de nome batem com sensores registrados para um prefixo específico
# Por exemplo, sensores de "anomalias", sensores de "movimento"
def truck_sensor_dict(registered_sensors, prefix, auth, ambiente="DEV"):

    url = "https://iot-backend.sapienz.alis.solutions/registry/automation/monitored_object/supermercadomundial" 

    response = requests.request("GET", url, headers=auth, data={})
    consulta = response.json()
    veiculo_id = {}
    
    for item in consulta["items"]:
        truck_data = item["customData"]
        frota = truck_data["fleet_number"]
        compound_id = item["compoundId"]
        identifier = compound_id["identifier"]
        if frota != '': veiculo_id[frota] = identifier

    sensores = {}
    for frota in veiculo_id:
        sensor_name = prefix + veiculo_id[frota]
        if sensor_name in registered_sensors:
            sensores[frota] = sensor_name

    return sensores

# Envia para um numero de sensores, dados de um dataframe "source", das colunas "metric"
# Sensores são um dicionário de chave numérica igual ao número de frota cujo conteúdo é o código do sensor na plataforma
def send_data(sensores, source, metric, auth, ambiente="DEV"):
    url = "https://automation.sapienz.alis.solutions/signal/v2/supermercadomundial"

    # Agrupa por frota
    for frota, data in source.groupby("vehicle_number"):
        print(frota, sensores)
        frota = str(frota)
        if frota in sensores:

            package = []
            # Itera por linha
            for _, row in data.iterrows(): 
                
                # Recupera métrica e timestamp
                value = float(row[metric])
                timestamp = int(row['timestamp'])
                package.append(
                    {
                        "id": str(sensores[frota]), #nome do sensor
                        "timestamp": timestamp,
                        "variables": [
                            {
                                "variable": metric,
                                "value": value
                            }
                        ]
                    }
                )
                if len(package) >= 800:
                    payload = json.dumps(package)
                    response = requests.request("POST", url, headers=auth, data=payload)
                    package = []
                    print(sensores[frota])
                    print(payload)
                    print(response)
                    print(response.text)
            print(package)  
            payload = json.dumps(package)
            response = requests.request("POST", url, headers=auth, data=payload)
            print(sensores[frota])
            print(payload)
            print(response)
            print(response.text)

# Com um header contendo autorização, requisita os nomes de sensores válidos
def get_sensor_names(auth, ambiente='DEV'):
    url = "https://iot-backend.sapienz.alis.solutions/registry/automation/sensor/supermercadomundial"
    
    response = requests.request("GET", url, headers=auth, data={})
    response = response.json()
    sensor_names = []
    for i in response['items']:
        id = i['compoundId']['identifier']
        sensor_names.append(id)
    return sensor_names