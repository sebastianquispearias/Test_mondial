import pandas as pd
import numpy as np

def detect_maintenance(df_vehiculo, interval_size=5):
    """
    Recebe o DataFrame de um veículo e retorna um dicionário com:
      - 'resumo_nox': NOx ponderado por categoria (lenta, media, elevada)
      - 'requiere_manutencao': True se NOx_media < NOx_elevada, caso contrário False (ou np.nan se insuficiente)
      - 'intervalos': DataFrame com os dados de cada intervalo

    O processamento ignora os registros com 'filial' preenchido, elimina linhas com velocidade 0,
    recalcula a diferença de tempo entre registros e cria segmentos (reinicia a cada diferença > 5 minutos).
    Em seguida, subdivide cada segmento em intervalos de 'interval_size' elementos, calculando
    a média ponderada (usando time_diff_sec como peso) para velocidade e NOx.
    """
    df = df_vehiculo.copy()
    
      # 1. Filtrar según percentiles de la columna NOx (2.5% y 97.5%)
    nox_desc = df['NOx'].describe(percentiles=[0.025, 0.975])
    nox_lower = nox_desc['2.5%']
    nox_upper = nox_desc['97.5%']
    print("\nFiltro de NOx por percentiles:")
    print(" - Percentil 2.5%:", nox_lower)
    print(" - Percentil 97.5%:", nox_upper)
    df = df[(df['NOx'] >= nox_lower) & (df['NOx'] <= nox_upper)]
    print("   Forma luego de filtrar NOx por percentiles:", df.shape)
    print(df.head(5).to_string())
    
    # 2. Filtrar según percentiles de la columna NOx_dp (2.5% y 97.5%)
    nox_dp_desc = df['NOx_dp'].describe(percentiles=[0.025, 0.975])
    nox_dp_lower = nox_dp_desc['2.5%']
    nox_dp_upper = nox_dp_desc['97.5%']
    print("\nFiltro de NOx_dp por percentiles:")
    print(" - Percentil 2.5%:", nox_dp_lower)
    print(" - Percentil 97.5%:", nox_dp_upper)
    df = df[(df['NOx_dp'] >= nox_dp_lower) & (df['NOx_dp'] <= nox_dp_upper)]
    print("   Forma luego de filtrar NOx_dp por percentiles:", df.shape)
    print(df.head(5).to_string())
    
    # 3. Filtrar valores de NOx mayores a 1500
    print("\nEliminación de valores de NOx mayores a 1500")
    df = df[df['NOx'] <= 1500]
    print("   Forma luego de eliminar NOx > 1500:", df.shape)
    print(df.head(5).to_string())
    

    # Ignorar registros com 'filial' preenchido
    df = df[df['filial'].isnull() | (df['filial'].str.strip() == "")]
    print("2. Después de filtrar 'filial' (vacío), forma:", df.shape)
    if df.empty:
        print("No hay datos después del filtro de 'filial'.")
        return {'resumo_nox': {}, 'requiere_manutencao': np.nan, 'intervalos': pd.DataFrame()}
    
    # eliminar
    print("\n[ELIMINAR/no considerar 2.5 %  cola izquierda cola derecha ]")
    print("\n[ELIMINAR/no considerar valoresde NOX mayores a 1500 ")

    # Eliminar linhas com velocidade zero
    df = df[df['velocidad_kmh'] > 0].copy()
    print("3. Después de eliminar velocidades 0, forma:", df.shape)

    # Converter timestamp para datetime (assume que o timestamp está em milissegundos)
    df['ts_dt'] = pd.to_datetime(df['timestamp'], unit='ms')
    print("4. Timestamps convertidos a datetime. Ejemplo:")
    print(df[['timestamp', 'ts_dt']].head())

    # Calcular a diferença de tempo entre registros e criar a coluna 'time_diff'
    df['time_diff'] = df['ts_dt'].diff(-1).abs()
    print("5. Calculadas las diferencias de tiempo. Ejemplo:")
    print(df[['ts_dt', 'time_diff']].head())
    
    # Criar segmento: reinicia sempre que a diferença for >5 minutos
    df['segment'] = (df['time_diff'] > pd.Timedelta(minutes=5)).cumsum()
    print("6. Segmentos asignados. Conteo de segmentos:")
    print(df['segment'].value_counts())

    # Converter a diferença de tempo para segundos
    df['time_diff_sec'] = df['time_diff'].dt.total_seconds().fillna(0)
    print("7. Diferencias de tiempo en segundos. Ejemplo:")
    print(df[['time_diff', 'time_diff_sec']].head())
####################
    # Dentro de cada segmento, agrupar a cada 'interval_size' elementos
    df['interval'] = df.groupby('segment').cumcount() // interval_size
    print("8. Asignación de intervalos. Muestra de datos:")
    print(df[['segment', 'interval']].head(15))

    # Calcular, para cada intervalo, a soma dos tempos e os valores ponderados de velocidade e NOx
    #### intervalos aca tienen q ser calculados agrupando cada vez que hayan 5 filas consecutivas con la misma clasificacion tanto para lento medio y elevada. y el valor 
    intervalos = df.groupby(['segment', 'interval']).apply(lambda g: pd.Series({
        'sum_time': g['time_diff_sec'].sum(),
        'vel_ponderada': np.average(g['velocidad_kmh'], weights=g['time_diff_sec']) if g['time_diff_sec'].sum() > 0 else np.nan,
        'nox_ponderada': np.average(g['NOx'], weights=g['time_diff_sec']) if g['time_diff_sec'].sum() > 0 else np.nan
    })).reset_index()
    print("9. Resultados de intervalos con promedios ponderados. Ejemplo:")
    print(intervalos.head())

    # Função para classificar a velocidade
    def clasificar(vel):
        if vel < 30:
            return 'lenta'
        elif vel < 60:
            return 'media'
        else:
            return 'elevada'
    
    intervalos['clasificacao'] = intervalos['vel_ponderada'].apply(clasificar)
    print("10. Clasificación de velocidades aplicada. Distribución:")
    print(intervalos['clasificacao'].value_counts())
    

    # Agregar intervalos por categoria para calcular o NOx médio ponderado
    resumo = intervalos.groupby('clasificacao').apply(
        lambda g: np.average(g['nox_ponderada'], weights=g['sum_time']) if g['sum_time'].sum() > 0 else np.nan
    ).to_dict()
    print("11. Resumen NOx por categoría:", resumo)

    # (Opcional) Mediana para análise futura:
    # mediana = intervalos.groupby('clasificacao')['nox_ponderada'].median().to_dict()
    
    if 'media' in resumo and 'elevada' in resumo:
        requiere = resumo['media'] < resumo['elevada']
    else:
        requiere = np.nan
    print("12. Requiere mantenimiento (True si NOx 'media' < 'elevada'):", requiere)
    

    resultado = {
        'resumo_nox': resumo,
        # 'mediana_nox': mediana,  # Descomentar se necessário
        'requiere_manutencao': requiere,
        'intervalos': intervalos
    }
    
    return resultado
