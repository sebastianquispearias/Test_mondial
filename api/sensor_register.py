import requests
import json

def create_sensor(sensor_names, auth, ambiente='DEV'):
    url = "https://iot-backend.sapienz.alis.solutions/registry/automation/sensor/supermercadomundial" #prod
    
    for sensor in sensor_names:
        payload = json.dumps({
            "customData": {},
            "compoundId": {
                "domainId": "whitemartins",
                "identifier": sensor
            },
            "providerId": "alisv2",
            "metricSourceIdentifier": sensor
        })
        response = requests.request("POST", url, headers=auth, data=payload)
        print(response.text)

def pick_type_and_template(metric):
    if metric == "parado":
        metricSourceTypeIdentifier = 'wm_Deteccao_Movimento_'
        metricSourceTemplateIdentifier = 'Deteccao_Movimento_'
    else:
        metricSourceTypeIdentifier = 'wm_Anomalias_Combustivel'
        metricSourceTemplateIdentifier = 'Anomalias_Combustivel'
    return metricSourceTypeIdentifier, metricSourceTemplateIdentifier

def sensor_to_monitored_object(sensor_names, monitored_object_names, metric, auth, ambiente='DEV'):
    url = "https://iot-backend.sapienz.alis.solutions/registry/automation/metric_source/supermercadomundial"

    metricSourceTypeIdentifier, metricSourceTemplateIdentifier = pick_type_and_template(metric)    
    for sensor, vehicle in zip(sensor_names, monitored_object_names):    
        print("Nome do sensor = %s e Veiculo = %s"%(sensor,vehicle))
        payload = json.dumps({
            "customData": {},
            "compoundId": {
                "domainId": "whitemartins",
                "identifier": sensor
            },
            "metricSourceTypeIdentifier": metricSourceTypeIdentifier,
            "monitoredObjectIdentifier": vehicle,
            "metricSourceTemplateIdentifier": metricSourceTemplateIdentifier,
            "sensorId": sensor,
            "isAnalyticsGenerated": False,
            "lastTimestampShouldConsiderAllMetrics": False
        })
        response = requests.request("POST", url, headers=auth, data=payload)
        print(response.text)


def pick_metric_source_template(metric):
    if metric == "parado":
        metricSourceTemplateAndMetricSourceIdentifiers = 'Deteccao_Movimento'
    else:
        metricSourceTemplateAndMetricSourceIdentifiers = 'Anomalias_Combustivel'
    return metricSourceTemplateAndMetricSourceIdentifiers

def monitored_object_to_sensor(sensor_names, monitored_object_names, metric, auth, ambiente='DEV'):
    metricSourceTemplateAndMetricSourceIdentifiers = pick_metric_source_template(metric)

    for sensor, vehicle in zip(sensor_names, monitored_object_names):
        url = f'https://iot-backend.sapienz.alis.solutions/registry/automation/monitored_object/supermercadomundial/{vehicle}' 
    
        print("Nome do sensor = %s e Veiculo = %s"%(sensor,vehicle))
        #GET
        response = requests.request("GET", url, headers=auth, data={})
        vehicle_object = response.json() 

        #UPDATE
        vehicle_object['metricSourceTemplateAndMetricSourceIdentifiers'][metricSourceTemplateAndMetricSourceIdentifiers] = sensor
        
        #RESEND
        payload = json.dumps(vehicle_object)
        response = requests.request("PUT", url, headers=auth, data=payload)
        print(response.text)


def sensor_metrics(metric='parado'):
    if metric=='parado':
        return [('parado', 'Deteccao de frota parada via NOx')]
    else:
        return [
            ('Ensemble Consumo','Deteccao de anomalia de consumo via Ensemble'),
            ('Ensemble Litros','Deteccao de anomalia de abastecimento via Ensemble'),
            ('Ensemble Km','Deteccao de anomalia de distância via Ensemble'),
            ('Ensemble NOx','Deteccao de anomalia de NOx via Ensemble'),
            ('Ensemble O2','Deteccao de anomalia de O2 via Ensemble')
        ]

# Cria lista de métricas
def get_metric_form(metric='parado'):
    metric_form = []
    metric_names = sensor_metrics(metric)
    for name, label in metric_names:
        object = {
            'name': name,
            'defaultLabel': label,
            'metricTypeIdentifier':'numeric'
        }
        metric_form.append(object)
    return metric_form

def get_identifier_and_default_label(metric='parado'):
    if metric=='parado':
        identifier = 'wm_Deteccao_Movimento'
        defaultLabel = 'Deteccao_Movimento'
        default_metric = 'parado'
    else:
        identifier = 'wm_Anomalias_Combustivel'
        defaultLabel = 'Anomalias_Combustivel'
        default_metric = 'Ensemble Consumo'
    return identifier, defaultLabel, default_metric

def push_metrics(sensor_names, metric, auth, ambiente='DEV'):
    identifier, defaultLabel, default_metric = get_identifier_and_default_label(metric)
    metric_form = get_metric_form(metric)
    url = "https://iot-backend.sapienz.alis.solutions/registry/automation/metric_source_type/supermercadomundial/" + identifier

    for sensor in sensor_names:
        print("Sensor = %s"%sensor)
        payload = json.dumps({
            "compoundId": {
                "domainId": "whitemartins",
                "identifier": identifier
            },
            "defaultLabel": defaultLabel,
            "defaultMetricName": default_metric,
            "metrics": metric_form
        })
        print(payload)

        response = requests.request("PUT", url, headers=auth, data=payload)
        print(response.text)