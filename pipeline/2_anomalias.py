import sys
import os
import pandas as pd
from preprocess.ensemble import VoteEnsemble
from math import radians, sin, cos, sqrt, atan2
import numpy as np
import matplotlib.pyplot as plt
#import seaborn as sns
from utils.geo_utils import haversine, 
from utils.maintenance import detectar_mantenimiento
from utils.geo_utils import extract_coordinates, filtrar_gps, obter_filial_con_estado

# Importar la lista de tiendas desde el archivo dados_rutas_lojas.py
from pipeline.dados_rutas_lojas import branches

# Verifica la existencia de archivos
path = "./"  
sys.path.append(path)

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
if nox_exists and abastecimento_exists and veiculos_exists:
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
if nox_exists:
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

    # 1. Eliminar filas con GPS inválido (0,0)
    gps_invalidos = nox[(nox['lat'] == 0) & (nox['lon'] == 0)]
    print(f"Filas con GPS inválido (0,0) eliminadas: {len(gps_invalidos)}")
    nox = nox[~((nox['lat'] == 0) & (nox['lon'] == 0))]

    # 2. Eliminar puntos fuera de Rio de Janeiro
    # Definir límites geográficos aproximados para Río
    lat_min, lat_max = -23.1, -22.56471809462388
    lon_min, lon_max = -43.8, -42.83667723331928 #-22.56471809462388, -42.83667723331928
    fuera_rio = nox[
        (nox['lat'] < lat_min) | (nox['lat'] > lat_max) |
        (nox['lon'] < lon_min) | (nox['lon'] > lon_max)
    ]
    print(f"Filas fuera de Río de Janeiro eliminadas: {len(fuera_rio)}")
    nox = nox[
        (nox['lat'] >= lat_min) & (nox['lat'] <= lat_max) &
        (nox['lon'] >= lon_min) & (nox['lon'] <= lon_max)
    ]

    nox = nox[~((nox['lat'] == 0) & (nox['lon'] == 0))].reset_index(drop=True)

    nox['timestamp_string'] = pd.to_datetime(nox['timestamp'], unit='ms')
    # Deja 'timestamp' como está (numérico), o si 'nox' originalmente tiene 'timestamp' como string,
    # conviértelo a numérico y guárdalo en 'timestamp'
    nox['timestamp'] = pd.to_numeric(nox['timestamp'], errors='coerce')

    
    # (Opcional: Ordenar por 'order' o por 'timestamp' si es necesario)
    # nox = nox.sort_values(by=['vehicle_number', 'timestamp'], ascending=[True, False])
    
    vehiculos_procesados = []
    
    # Procesar cada vehículo de forma separada
    for vehicle_id, df_vehiculo in nox.groupby('vehicle_number'):
        df_vehiculo = df_vehiculo.copy()  # Evitar modificar la vista original
        
        # Calcular la distancia entre puntos usando la fórmula de Haversine
        df_vehiculo['lat_prev'] = df_vehiculo['lat'].shift(periods=-1)
        df_vehiculo['lon_prev'] = df_vehiculo['lon'].shift(periods=-1)
        df_vehiculo['distancia_km'] = df_vehiculo.apply(
            lambda row: haversine(row['lat_prev'], row['lon_prev'], row['lat'], row['lon']), axis=1
        )
        # df_vehiculo['distancia_km'].fillna(-1, inplace=True)  # La primera distancia se establece en -1
        print("hola")
        # Calcular la diferencia de tiempo en segundos (usando diff con periods=-1 para datos en orden descendente)
        df_vehiculo['time_diff_sec'] = df_vehiculo['timestamp'].diff(periods=-1).abs() / 1000
        
        # Crear un flag si el tiempo entre filas es alto (por ejemplo, mayor a 480 segundos)
        df_vehiculo['flag_tiempo_alto'] = df_vehiculo['time_diff_sec'].apply(
            lambda x: 'Tiempo entre filas alto' if x > 600 else ''
        )
        
        # Calcular la velocidad (solo si time_diff_sec está entre 0 y 300 segundos)
        df_vehiculo['velocidad_kmh'] = df_vehiculo.apply(
            lambda row: row['distancia_km'] / (row['time_diff_sec'] / 3600)
            if (row['time_diff_sec'] > 0 and row['time_diff_sec'] <= 600) else 0,
            axis=1
        )
        
        # 3. Eliminar velocidades mayores a 150 km/h y debug
        velocidades_altas = df_vehiculo[df_vehiculo['velocidad_kmh'] > 150]
        if len(velocidades_altas) > 0:
            print(f"Vehículo {vehicle_id}: eliminadas {len(velocidades_altas)} filas por velocidad excesiva (>150 km/h)")
            print(velocidades_altas[['timestamp', 'velocidad_kmh', 'lat', 'lon']])


        # Asignar la filial basada en la posición (usando la función refactorizada)
        df_vehiculo['filial'] = df_vehiculo.apply(
            lambda row: obter_filial_con_estado(row['lat'], row['lon'], branches),
            axis=1
        )
        
        # Verificación temporal: conservar el flag "filial" solo si se tienen al menos 3 registros consecutivos,
        # o si, a pesar de ser un grupo pequeño, el tiempo máximo entre registros es mayor o igual a umbral_tiempo.
        min_consecutive = 3
        umbral_tiempo = 600  # 600 segundos = 10 minutos
        df_vehiculo['group_id'] = (df_vehiculo['filial'] != df_vehiculo['filial'].shift()).cumsum()
        
        def check_group(grupo):
            if grupo.iloc[0] != "":
                if len(grupo) < min_consecutive:
                    max_time = df_vehiculo.loc[grupo.index, 'time_diff_sec'].max()
                    if max_time >= umbral_tiempo:
                        return grupo.tolist()
                    else:
                        return [""] * len(grupo)
                else:
                    return grupo.tolist()
            else:
                return grupo.tolist()
        
        df_vehiculo['filial'] = df_vehiculo.groupby('group_id')['filial'].transform(check_group)
        df_vehiculo.drop(columns="group_id", inplace=True)
        
        # Ahora, forzar la velocidad a 0 en los registros confirmados como parada en filial
        df_vehiculo.loc[df_vehiculo['filial'] != "", 'velocidad_kmh'] = 0
        
        # Clasificar la velocidad para análisis posterior
        def clasificar_velocidad(velocidad):
            if velocidad < 30:
                return 'lenta'
            elif 30 <= velocidad < 60:
                return 'media'
            else:
                return 'elevada'
        
        df_vehiculo['clasificacion_velocidad'] = df_vehiculo['velocidad_kmh'].apply(clasificar_velocidad)
        
        vehiculos_procesados.append(df_vehiculo)
    
    nox_procesado = pd.concat(vehiculos_procesados, ignore_index=True)
    print(f"DataFrame de NOx processado: {nox_procesado.shape[0]} filas")
    
        
    nox_procesado.to_csv(path + "anomalias/nox.csv", index=False)
    print("Arquivo anomalias/nox.csv gerado com sucesso")