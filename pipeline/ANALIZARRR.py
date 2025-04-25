import os
import sys
print("CWD:", os.getcwd())
print("sys.path:", sys.path)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
#sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import pandas as pd
from preprocess.ensemble import VoteEnsemble
from math import radians, sin, cos, sqrt, atan2
import numpy as np
import matplotlib.pyplot as plt
from utils.maintenance import detect_maintenance
from utils.geo_utils import haversine, extract_coordinates, filtrar_gps, obter_filial_con_estado
from utils.vehicle_processing import procesar_vehiculo, imputar_rota
from utils.plotting import plot_boxplot_intervals_with_weighted_mean, gerar_histogramas_consumo
from utils.export import export_maintenance_summary_csv, export_maintenance_results_excel
from preprocess.movement import stopped_df
from utils.dados_rutas_lojas import branches
# Verifica la existencia de archivo
path = "./"  
sys.path.append(path)

executeAbastecimento = os.getenv("EXECUTE_ABASTECIMENTO", "False").lower() == "true"
executeNox = os.getenv("EXECUTE_NOX","False").lower() == "true"

###########
executeAbastecimento = True
executeNox = True
#########

if not os.path.exists(path + "dados limpos/"):
    os.makedirs(path + "dados limpos/")
if not os.path.exists(path + "anomalias/"):
    os.makedirs(path + "anomalias/")
if not os.path.exists(path + "dados limpos/invalidos/"):
    os.makedirs(path + "dados limpos/invalidos/")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
path = os.path.join(BASE_DIR, "")

nox_exists = os.path.exists(path + "dados limpos/nox.csv")
print("nox_exists:", nox_exists)
abastecimento_exists = os.path.exists(path + "dados limpos/abastecimentos.csv")
veiculos_exists = os.path.exists(path + "dados/informacoes_veiculos.csv")
abastecimento_invalidos_path = path + "dados limpos/invalidos/invalid_consumption.csv"

############################################################################################
# Procesar abastecimento
############################################################################################
if executeAbastecimento :
    veiculos = pd.read_csv(path + "dados/informacoes_veiculos.csv")

    # --- LECTURA CORRECTA DEL CSV ---
    abastecimento = pd.read_csv(
        os.path.join(path, "dados limpos/abastecimentosVALIDO_USAR_EXCEL.csv"),
        sep=';',                     # <- aquí
        engine='python',             # para manejar comillas complejas si las hay
        skipinitialspace=True        # elimina espacios tras los separadores
    )

    # Si sobra una columna vacía, la descartas:
    if '' in abastecimento.columns:
        abastecimento = abastecimento.drop(columns=[''])
    
    
    df_vehiculo_121 = abastecimento[abastecimento['vehicle_number'] == 121]
    gerar_histogramas_consumo(df_vehiculo_121, vehicle_number=121)

    # --- AGRUPAR Y GRAFICAR para cada vehículo ---
    for vehicle_id, df_vehiculo in abastecimento.groupby('vehicle_number'):
        # Llamamos a la función con el subconjunto correcto:
        gerar_histogramas_consumo(df_vehiculo, vehicle_number=vehicle_id)