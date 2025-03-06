import os
import sys
import pandas as pd
from datetime import datetime
import time

# TODO: Improve imports, use absolute path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(root_dir)

from api import send_api

file_name = os.path.basename(__file__)

def log_message(message):
    print(f"[{file_name}]: {message}")

def log_error(message):
    print(f"[{file_name} - ERROR]: {message}")


# TODO: FIX method
def log(df, log_folder='log/'):
    if not os.path.exists(path): os.makedirs(path)
    for number, data in df.groupby('vehicle_number'):
        # print(data[metric])
        data[metric] = data[metric]
        data['Datas'] = pd.to_datetime(data['timestamp'], unit='ms').dt.strftime('%d/%m/%Y %H:%M:%S')
        data['Metrica'] = metric
        if number in sensores:
            data['Sensor'] = sensores[number]
            data = data.set_index('timestamp')
            data.to_csv(path+f'{log_folder}/{prefix}{number}_{metric}.csv')

if __name__ == '__main__':
    path = './'
    sys.path.append(path)

    # Troca das datas hardcoded por var de ambiente 
    start = os.getenv("START_DATE", "06/09/2024")
    end = os.getenv("FINISH_DATE", "13/09/2024")
    
    executeAbastecimento = os.getenv("EXECUTE_ABASTECIMENTO", "False").lower() == "true"    
    executeNox = os.getenv("EXECUTE_NOX", "False").lower() == "true"

    with open(path + 'token') as file: token = file.read()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # Métricas dos sensores associadas aos prefixos
    metrics = dict()

    if executeAbastecimento:
        # metrics_abastecimento
        metrics = {
            "anomaly_consumption": "Anomalias_Combustivel_",
            "anomaly_liter_supply": "Anomalias_Combustivel_",
            "anomaly_km_driven": "Anomalias_Combustivel_"
        }
        print("Iniciando upload Abastecimento")

    if executeNox:
        # metrics_nox
        metrics = {
            "label_parado_nox": "Deteccao_Movimento_",
            "anomaly_nox": "Anomalias_Combustivel_",
            "anomaly_o2": "Anomalias_Combustivel_"
        }
        print("Iniciando upload NOx")


    if len(metrics) == 0:
        log_error("executeNox and executeAbastecimento are both false.")
    else:
        # Lista se sensores registrados
        registered_sensors = send_api.get_sensor_names(auth=headers, ambiente='PROD')
        print(registered_sensors)

        start = time.mktime(datetime.strptime(start, "%d/%m/%Y").timetuple())
        start *= 1000
        end = time.mktime(datetime.strptime(end, "%d/%m/%Y").timetuple())
        end *= 1000

        for metric, prefix in metrics.items():
            # Recupera a metrica da fonte
            df, metric = send_api.retrieve_metric(path, metric)
            condition = (df['timestamp'] > start) & (df['timestamp'] < end)
            df = df[condition]
            if len(df) > 0:
                print(len(df))

                # Estabelece a lista de sensores
                sensores = send_api.truck_sensor_dict(registered_sensors, prefix, auth=headers, ambiente='PROD')
                # print(sensores)
                #     log(df)

                # Envia da fonte aos sensores
                send_api.send_data(sensores, source=df, metric=metric, auth=headers, ambiente='PROD')







