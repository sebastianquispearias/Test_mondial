import pandas as pd
from math import radians, sin, cos, sqrt, atan2
from utils.geo_utils import haversine, obter_filial_con_estado

def procesar_vehiculo(df_vehiculo, vehicle_id, branches, min_consecutive=3, umbral_tiempo=600):
    """
    Processa os dados de um veículo:
      - Calcula a distância entre pontos utilizando a fórmula de Haversine.
      - Calcula a diferença de tempo (em segundos) entre registros.
      - Cria um flag se o tempo entre registros é maior que o umbral.
      - Calcula a velocidade (km/h) para intervalos de tempo aceitáveis.
      - Remove registros com velocidade excessiva (>150 km/h) e imprime debug.
      - Atribui a filial baseada na posição usando a função obter_filial_con_estado.
      - Agrupa registros consecutivos para manter a filial somente se houver pelo menos min_consecutive registros,
        ou se o tempo máximo entre eles for alto.
      - Força a velocidade a 0 onde a filial foi atribuída e classifica a velocidade.
      
    Retorna o DataFrame processado para o veículo.
    """
    df_vehiculo['lat_prev'] = df_vehiculo['lat'].shift(-1)
    df_vehiculo['lon_prev'] = df_vehiculo['lon'].shift(-1)
    df_vehiculo['distancia_km'] = df_vehiculo.apply(
        lambda row: haversine(row['lat_prev'], row['lon_prev'], row['lat'], row['lon']),
        axis=1
    )
    # Calcular a diferença de tempo em segundos (assumindo que 'timestamp' está em milissegundos)
    df_vehiculo['time_diff_sec'] = df_vehiculo['timestamp'].diff(-1).abs() / 1000.0
    # Flag para intervalos de tempo altos
    df_vehiculo['flag_tiempo_alto'] = df_vehiculo['time_diff_sec'].apply(
        lambda x: 'Tempo entre registros alto' if x > umbral_tiempo else ''
    )
    # Calcular a velocidade (km/h) quando o intervalo de tempo é aceitável
    df_vehiculo['velocidad_kmh'] = df_vehiculo.apply(
        lambda row: row['distancia_km'] / (row['time_diff_sec'] / 3600)
        if (row['time_diff_sec'] > 0 and row['time_diff_sec'] <= umbral_tiempo) else 0,
        axis=1
    )



    # Remover registros com velocidade > 150 km/h e mostrar debug
    velocidades_altas = df_vehiculo[df_vehiculo['velocidad_kmh'] > 150]
    if len(velocidades_altas) > 0:
        print(f"Vehículo {vehicle_id}: eliminadas {len(velocidades_altas)} filas por velocidad excesiva (>150 km/h)")
        print(velocidades_altas[['timestamp', 'velocidad_kmh', 'lat', 'lon']])
    # Atribuir a filial baseada na posição
    df_vehiculo['filial'] = df_vehiculo.apply(
        lambda row: obter_filial_con_estado(row['lat'], row['lon'], branches),
        axis=1
    )
    
    # Agrupar registros consecutivos para manter a filial
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
   ########################## 
    df_vehiculo['filial'].replace("", pd.NA, inplace=True)
   ############### 
    # Criar colunas auxiliares usando ffill (valor acima) e bfill (valor abaixo)
    df_vehiculo['filial_arriba'] = df_vehiculo['filial'].ffill()   # valor mais atual (acima)
    df_vehiculo['filial_abajo']  = df_vehiculo['filial'].bfill()    # valor mais antigo (abaixo)
    
    # Para cada linha com filial NA, preencher com a string formatada:
    # "rota entre [filial_abajo] ate [filial_arriba]"
    mask = df_vehiculo['filial'].isna()
    df_vehiculo.loc[mask, 'filial'] = (
         "Rota entre " +
         df_vehiculo.loc[mask, 'filial_abajo'] +
         " até " +
         df_vehiculo.loc[mask, 'filial_arriba']
    )
    
    # Remover as colunas auxiliares
    df_vehiculo.drop(['filial_arriba', 'filial_abajo'], axis=1, inplace=True)
#############
    # Forçar velocidade 0 onde a filial foi atribuída
    df_vehiculo.loc[df_vehiculo['filial'] != "", 'velocidad_kmh'] = 0
    
    def clasificar_velocidade(vel):
        if vel < 30:
            return 'lenta'
        elif 30 <= vel < 60:
            return 'media'
        else:
            return 'elevada'
    df_vehiculo['clasificacion_velocidade'] = df_vehiculo['velocidad_kmh'].apply(clasificar_velocidade)
    
    return df_vehiculo
