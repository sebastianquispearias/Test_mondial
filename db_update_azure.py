import pandas as pd
from sqlalchemy import create_engine

# Cria uma conexão com o banco de dados PostgreSQL no Azure
engine = create_engine('postgresql://zane:UkP8JfR*@db-dev-zane.postgres.database.azure.com:5432/zane-teste')

# Lê os arquivos CSV em DataFrames
df_informacoes_veiculos = pd.read_csv(r'dados/informacoes_veiculos.csv', delimiter=',')
df_nox = pd.read_csv(r'dados/nox.csv', delimiter=',')
df_nox_parado = pd.read_csv(r'parado/nox.csv', delimiter=',')
df_nox_limpos = pd.read_csv(r'dados limpos/nox.csv', delimiter=',')
df_anomalias_nox = pd.read_csv(r'anomalias/nox.csv', delimiter=',')
df_abastecimentos = pd.read_csv(r'dados/abastecimentos.csv', delimiter=',')
df_abastecimentos_limpos = pd.read_csv(r'dados limpos/abastecimentos.csv', delimiter=',')
df_anomalias_abastecimentos = pd.read_csv(r'anomalias/abastecimentos.csv', delimiter=',')

# Renomeia as colunas dos DataFrame (apenas necessário nos de NOx) conforme as tabelas
df_nox.rename(columns={
    'order': 'ordem',
    'Sensor_Hours': 'sensor_hours',
    'NOx': 'nox',
    'NOx_max': 'nox_max',
    'NOx_min': 'nox_min',
    'NOx_dp': 'nox_dp',
    'O2': 'o2',
    'position': 'position_gps'
}, inplace=True)

df_nox_parado.rename(columns={
    'order': 'ordem',
    'Sensor_Hours': 'sensor_hours',
    'NOx': 'nox',
    'NOx_max': 'nox_max',
    'NOx_min': 'nox_min',
    'NOx_dp': 'nox_dp',
    'O2': 'o2',
    'position': 'position_gps'
}, inplace=True)

df_nox_limpos.rename(columns={
    'order': 'ordem',
    'Sensor_Hours': 'sensor_hours',
    'NOx': 'nox',
    'NOx_max': 'nox_max',
    'NOx_min': 'nox_min',
    'NOx_dp': 'nox_dp',
    'O2': 'o2',
    'position': 'position_gps'
}, inplace=True)

df_anomalias_nox.rename(columns={
    'order': 'ordem',
    'Sensor_Hours': 'sensor_hours',
    'NOx': 'nox',
    'NOx_max': 'nox_max',
    'NOx_min': 'nox_min',
    'NOx_dp': 'nox_dp',
    'O2': 'o2',
    'position': 'position_gps'
}, inplace=True)

# Escreve os DataFrames nas tabelas PostgreSQL, substituindo as tabelas existentes
df_informacoes_veiculos.to_sql('mundial_informacoes_veiculos', engine, schema='public', if_exists='replace', index=False)
print("Tabela mundial_informacoes_veiculos atualizada com sucesso")

df_nox.to_sql('mundial_nox', engine, schema='public', if_exists='replace', index=False)
print("Tabela mundial_nox atualizada com sucesso")

df_nox_parado.to_sql('mundial_nox_parado', engine, schema='public', if_exists='replace', index=False)
print("Tabela mundial_nox_parado atualizada com sucesso")

df_nox_limpos.to_sql('mundial_nox_limpos', engine, schema='public', if_exists='replace', index=False)
print("Tabela mundial_nox_limpos atualizada com sucesso")

df_anomalias_nox.to_sql('mundial_anomalias_nox', engine, schema='public', if_exists='replace', index=False)
print("Tabela mundial_anomalias_nox atualizada com sucesso")

df_abastecimentos.to_sql('mundial_abastecimentos', engine, schema='public', if_exists='replace', index=False)
print("Tabela mundial_abastecimentos atualizada com sucesso")

df_abastecimentos_limpos.to_sql('mundial_abastecimentos_limpos', engine, schema='public', if_exists='replace', index=False)
print("Tabela mundial_abastecimentos_limpos atualizada com sucesso")

df_anomalias_abastecimentos.to_sql('mundial_anomalias_abastecimentos', engine, schema='public', if_exists='replace', index=False)
print("Tabela mundial_anomalias_abastecimentos atualizada com sucesso")