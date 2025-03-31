import pandas as pd

def detectar_mantenimiento(df):
    """
    A partir de um df contendo as colunas 'vehicle_number', 'clasificacion_velocidad'
    e 'NOx', agrupa os dados e calcula a média de NOx por veículo e classificação.
    
    Considera que um veículo requer manutenção se: média de NOx na categoria 'elevada' > NOx na categoria 'media'.
    
    Retorna um DataFrame com as colunas 'vehicle_number' e 'requiere_mantenimiento'.
    """
    agrupado = df.groupby(['vehicle_number', 'clasificacion_velocidad'])['NOx'].mean().unstack()
    # Verifica se as colunas 'elevada' e 'media' existem
    if 'elevada' not in agrupado.columns or 'media' not in agrupado.columns:
        print("Aviso: Faltam dados de 'elevada' ou 'media' no agrupamento.")
        return pd.DataFrame()
    agrupado['requiere_mantenimiento'] = agrupado['elevada'] > agrupado['media']
    resultado = agrupado[agrupado['requiere_mantenimiento']].reset_index()
    return resultado[['vehicle_number', 'requiere_mantenimiento']]
