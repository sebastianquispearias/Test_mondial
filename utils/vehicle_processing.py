# utils/vehicle_processing.py
import pandas as pd
from math import radians, sin, cos, sqrt, atan2

# Asegúrate de importar las funciones de geo que ya tengas,
# por ejemplo, si ya tienes haversine y obter_tienda_con_estado en utils/geo_utils.py:
from utils.geo_utils import haversine, obter_tienda_con_estado

def procesar_vehiculo(df_vehiculo, vehicle_id, branches, min_consecutive=3, umbral_tiempo=600):
    """
    Procesa los datos de un vehículo:
      - Calcula la distancia entre puntos utilizando la fórmula de Haversine.
      - Calcula la diferencia de tiempo (en segundos) entre registros.
      - Crea un flag si el tiempo entre filas es mayor que umbral.
      - Calcula la velocidad (km/h) para intervalos de tiempo aceptables.
      - Elimina filas con velocidades excesivas (>150 km/h) y muestra debug info.
      - Asigna el flag 'tienda' según la posición usando la función obter_tienda_con_estado.
      - Realiza un ajuste en la asignación de la tienda para conservarla solo si hay al menos
        min_consecutive registros consecutivos o el tiempo máximo entre ellos es alto.
      - Forza la velocidad a 0 en los registros con tienda asignada y clasifica la velocidad.
      
    Parámetros:
      df_vehiculo: DataFrame con los datos del vehículo.
      vehicle_id: Identificador del vehículo (para debug).
      branches: Lista de tiendas (filiales) para geofencing.
      min_consecutive: Número mínimo de registros consecutivos para conservar el flag.
      umbral_tiempo: Tiempo (en segundos) a partir del cual se considera alto el intervalo.
      
    Retorna:
      DataFrame procesado para el vehículo.
    """
    # Calcular la distancia entre puntos
    df_vehiculo['lat_prev'] = df_vehiculo['lat'].shift(-1)
    df_vehiculo['lon_prev'] = df_vehiculo['lon'].shift(-1)
    df_vehiculo['distancia_km'] = df_vehiculo.apply(
        lambda row: haversine(row['lat_prev'], row['lon_prev'], row['lat'], row['lon']),
        axis=1
    )
    print("hola")  # Debug
    # Calcular la diferencia de tiempo en segundos (suponiendo que 'timestamp' es numérico en milisegundos)
    df_vehiculo['time_diff_sec'] = df_vehiculo['timestamp'].diff(-1).abs() / 1000.0
    
    # Crear un flag si el tiempo entre filas es alto (mayor que umbral_tiempo)
    df_vehiculo['flag_tiempo_alto'] = df_vehiculo['time_diff_sec'].apply(
        lambda x: 'Tiempo entre filas alto' if x > umbral_tiempo else ''
    )
    
    # Calcular la velocidad (km/h) solo si time_diff_sec está entre 0 y umbral_tiempo
    df_vehiculo['velocidad_kmh'] = df_vehiculo.apply(
        lambda row: row['distancia_km'] / (row['time_diff_sec'] / 3600)
        if (row['time_diff_sec'] > 0 and row['time_diff_sec'] <= umbral_tiempo) else 0,
        axis=1
    )
    
    # Eliminar filas con velocidad mayor a 150 km/h y mostrar información de depuración
    velocidades_altas = df_vehiculo[df_vehiculo['velocidad_kmh'] > 150]
    if len(velocidades_altas) > 0:
        print(f"Vehículo {vehicle_id}: eliminadas {len(velocidades_altas)} filas por velocidad excesiva (>150 km/h)")
        print(velocidades_altas[['timestamp', 'velocidad_kmh', 'lat', 'lon']])
    
    # Asignar el flag de tienda según la posición
    df_vehiculo['tienda'] = df_vehiculo.apply(
        lambda row: obter_tienda_con_estado(row['lat'], row['lon'], branches),
        axis=1
    )
    
    # Ajustar el flag "tienda" para conservarlo solo en grupos consecutivos
    df_vehiculo['group_id'] = (df_vehiculo['tienda'] != df_vehiculo['tienda'].shift()).cumsum()
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
    df_vehiculo['tienda'] = df_vehiculo.groupby('group_id')['tienda'].transform(check_group)
    df_vehiculo.drop(columns="group_id", inplace=True)
    
    # Forzar la velocidad a 0 en los registros donde se ha asignado una tienda
    df_vehiculo.loc[df_vehiculo['tienda'] != "", 'velocidad_kmh'] = 0
    
    # Clasificar la velocidad
    def clasificar_velocidad(vel):
        if vel < 30:
            return 'lenta'
        elif 30 <= vel < 60:
            return 'media'
        else:
            return 'elevada'
    df_vehiculo['clasificacion_velocidad'] = df_vehiculo['velocidad_kmh'].apply(clasificar_velocidad)
    
    return df_vehiculo
