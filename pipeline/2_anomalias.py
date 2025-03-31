import sys
import os
import pandas as pd
from preprocess.ensemble import VoteEnsemble
from math import radians, sin, cos, sqrt, atan2
import numpy as np
import matplotlib.pyplot as plt
#import seaborn as sns
from utils.maintenance import detectar_mantenimiento
from utils.geo_utils import haversine, extract_coordinates, filtrar_gps, obter_filial_con_estado
from utils.vehicle_processing import procesar_vehiculo

# Importar la lista de tiendas desde el archivo dados_rutas_lojas.py
from pipeline.dados_rutas_lojas import branches

# Verifica la existencia de archivos
path = "./"  
sys.path.append(path)

executeAbastecimento = os.getenv("EXECUTE_ABASTECIMENTO", "False").lower() == "true"
executeNox = os.getenv("EXECUTE_NOX","False").lower() == "true"

##
executeAbastecimento = False
executeNox = True
##

if not os.path.exists(path + "dados limpos/"):
    os.makedirs(path + "dados limpos/")
if not os.path.exists(path + "anomalias/"):
    os.makedirs(path + "anomalias/")
if not os.path.exists(path + "dados limpos/invalidos/"):
    os.makedirs(path + "dados limpos/invalidos/")


nox_exists = os.path.exists(path + "dados limpos/nox.csv")
print("nox_exists:", nox_exists)
abastecimento_exists = os.path.exists(path + "dados limpos/abastecimentos.csv")
veiculos_exists = os.path.exists(path + "dados/informacoes_veiculos.csv")
abastecimento_invalidos_path = path + "dados limpos/invalidos/invalid_consumption.csv"

############################################################################################
# Procesar abastecimento
############################################################################################
if executeAbastecimento :
    nox = pd.read_csv(path + "dados limpos/nox.csv")
    print("DataFrame de nox limpos:", nox.shape)
    veiculos = pd.read_csv(path + "dados/informacoes_veiculos.csv")
    abastecimento = pd.read_csv(path + "dados limpos/abastecimentos.csv")
    abastecimento_invalido = pd.read_csv(abastecimento_invalidos_path)
    
    # Agregar la columna `vehicle_type` únicamente
    veiculos = veiculos[["fleet_number", "vehicle_type"]].rename(columns={"fleet_number": "vehicle_number"})
    abastecimento = abastecimento.merge(veiculos, on="vehicle_number", how="left")
    abastecimento_invalido = abastecimento_invalido.merge(veiculos, on="vehicle_number", how="left")
    
    # Detectar anomalías
    clf = VoteEnsemble()
    
    # Entrenar con `abastecimento` y predecir 
    clf.fit(abastecimento["km_driven"])
    abastecimento["anomaly_km_driven"] = clf.predict(abastecimento["km_driven"])
    if not abastecimento_invalido.empty:
        abastecimento_invalido["anomaly_km_driven"] = clf.predict(abastecimento_invalido["km_driven"])
    
    clf.fit(abastecimento["consumption"])
    abastecimento["anomaly_consumption"] = clf.predict(abastecimento["consumption"])
    if not abastecimento_invalido.empty:
        abastecimento_invalido["anomaly_consumption"] = clf.predict(abastecimento_invalido["consumption"])
    
    clf.fit(abastecimento["liter_supply"])
    abastecimento["anomaly_liter_supply"] = clf.predict(abastecimento["liter_supply"])
    if not abastecimento_invalido.empty:
        abastecimento_invalido["anomaly_liter_supply"] = clf.predict(abastecimento_invalido["liter_supply"])
    
    # Combinar datos válidos e inválidos y guardar
    abastecimento = pd.concat([abastecimento, abastecimento_invalido], ignore_index=True)
    abastecimento = abastecimento.replace({True: 1, False: 0})
    abastecimento.to_csv(path + "anomalias/abastecimentos.csv", index=False)

############################################################################################
# Procesar NOx
############################################################################################
if executeNox:
    # Cargar datos
    nox = pd.read_csv(path + "dados limpos/nox.csv")
    
    # Detectar anomalías
    clf = VoteEnsemble()
    nox['anomaly_nox'] = clf.fit_predict(nox['NOx'])
    nox['anomaly_o2'] = clf.fit_predict(nox['O2'])
    
    # Extraer coordenadas de la columna 'position'
    nox = extract_coordinates(nox)
        
    # --- DEBUG INFO ---
    total_inicial = len(nox)
    print(f"Total filas iniciales: {total_inicial}")


    nox = filtrar_gps(nox, lat_min=-23.1, lat_max=-22.56471809462388, lon_min=-43.8, lon_max=-42.83667723331928)


    nox['timestamp_string'] = pd.to_datetime(nox['timestamp'], unit='ms')
    
    # eliminar? 
    nox['timestamp'] = pd.to_numeric(nox['timestamp'], errors='coerce')

    
    # (Opcional: Ordenar por 'order' o por 'timestamp' si es necesario)
    # nox = nox.sort_values(by=['vehicle_number', 'timestamp'], ascending=[True, False])
    
    vehiculos_procesados = []
    
    ######## Procesar cada vehículo de forma separada
    for vehicle_id, df_vehiculo in nox.groupby('vehicle_number'):
        df_vehiculo = df_vehiculo.copy()
        df_vehiculo = procesar_vehiculo(df_vehiculo, vehicle_id, branches, min_consecutive=3, umbral_tiempo=600)
        vehiculos_procesados.append(df_vehiculo)
    
    nox_procesado = pd.concat(vehiculos_procesados, ignore_index=True)
    print(f"DataFrame de NOx processado: {nox_procesado.shape[0]} filas")
    
        
    nox_procesado.to_csv(path + "anomalias/nox.csv", index=False)
    print("Arquivo anomalias/nox.csv gerado com sucesso")