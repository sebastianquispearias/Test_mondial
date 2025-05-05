import os
import pandas as pd
from preprocess.ensemble import VoteEnsemble
from preprocess.movement import stopped_df
from utils.maintenance import detect_maintenance
from utils.geo_utils import extract_coordinates, filtrar_gps
from utils.vehicle_processing import procesar_vehiculo, imputar_rota
from utils.export import export_maintenance_summary_csv
from utils.dados_rutas_lojas import branches

def process_nox(base_dir, raw_dir, anomalies_dir):
    """
    Detecta anomalias de NOx:
    - Carrega dados de NOx limpos.
    - Converte timestamp e cria coluna de string.
    - Executa VoteEnsemble, filtra GPS, marca paradas e preenche rota.
    - Detecta manutenção por veículo e salva resumo + CSV final.
    """
    path_nox = os.path.join(raw_dir, "nox.csv")
    if not os.path.exists(path_nox):
        print(f"[ERRO] Arquivo não encontrado: {path_nox}")
        return

    print(f"[INFO] Carregando NOx de: {path_nox}")
    nox = pd.read_csv(path_nox)

    # 1) Detectar anomalias via ensemble
    clf = VoteEnsemble()
    nox['anomaly_nox'] = clf.fit_predict(nox['NOx'])
    nox['anomaly_o2']  = clf.fit_predict(nox['O2'])

    # 2) Extrair coordenadas de position
    nox = extract_coordinates(nox)

    # Debug: mostrar total inicial
    total_inicial = len(nox)
    print(f"Total filas iniciales: {total_inicial}")

    # 3) Filtrar GPS fora de área
    nox = filtrar_gps(
        nox,
        lat_min=-23.1,  lat_max=-22.56471809462388,
        lon_min=-43.8,  lon_max=-42.83667723391928
    )

    # 4) Converter timestamps
    nox['timestamp_string'] = pd.to_datetime(nox['timestamp'], unit='ms')
    nox['timestamp']        = pd.to_numeric(nox['timestamp'], errors='coerce')

    maintenance_results  = []
    vehiculos_procesados = []

    for vehicle_id, df_vehiculo in nox.groupby('vehicle_number'):
        df_vehiculo = df_vehiculo.copy()

        # 5) Processar rota e velocidade
        df_vehiculo = procesar_vehiculo(
            df_vehiculo, vehicle_id, branches,
            min_consecutive=3, umbral_tiempo=600
        )

        # 6) Salvar antes de stopped
        df_vehiculo.to_csv(
            os.path.join(anomalies_dir, "df_vehiculo_sin_stopped.csv"),
            index=False
        )

        # 7) Identificar paradas
        df_vehiculo = stopped_df(df_vehiculo)
        # Para remover paradas, descomente:
        # df_vehiculo = df_vehiculo[~df_vehiculo['label_parado_nox']]
        df_vehiculo.to_csv(
            os.path.join(anomalies_dir, "df_vehiculo_despues_stopped.csv"),
            index=False
        )

        # 8) Detectar manutenção
        maintenance_result = detect_maintenance(df_vehiculo)
        print(f"Resultado de manutenção para o veículo {vehicle_id}:")
        print(maintenance_result)

        # 9) Preencher rota entre paradas
        df_vehiculo = imputar_rota(df_vehiculo)

        maintenance_results.append({
            "vehicle_number": vehicle_id,
            "resultado_manutencao": maintenance_result
        })
        vehiculos_procesados.append(df_vehiculo)
        print(f"[INFO] Veículo {vehicle_id} processado")

    # 10) Concatenar e exportar resumo
    nox_procesado = pd.concat(vehiculos_procesados, ignore_index=True)
    print(f"DataFrame de NOx processado: {nox_procesado.shape[0]} filas")

    summary_path = os.path.join(base_dir, "maintenance_summary.csv")
    export_maintenance_summary_csv(
        maintenance_results,
        output_filename=summary_path
    )

    # 11) Salvar CSV final de NOx
    out = os.path.join(anomalies_dir, "nox.csv")
    nox_procesado.to_csv(out, index=False)
    print(f"[INFO] CSV de NOx salvo em: {out}")
