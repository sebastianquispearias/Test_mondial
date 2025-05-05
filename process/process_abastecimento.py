import os
import pandas as pd
from preprocess.ensemble import VoteEnsemble

def process_abastecimento(base_dir, raw_dir, anomalies_dir):
    """
    Detecta anomalias no abastecimento:
    - Carrega dados de veículos e de abastecimento (limpos e inválidos).
    - Executa VoteEnsemble em km_driven, consumption e liter_supply.
    - Combina resultados e salva o CSV de anomalias.
    """
    path_veiculos          = os.path.join(base_dir, "dados", "informacoes_veiculos.csv")
    path_abastecimento     = os.path.join(raw_dir,  "abastecimento.csv")
    path_abastecimento_inv = os.path.join(raw_dir,  "invalidos", "invalid_consumption.csv")
    path_saida             = os.path.join(anomalies_dir, "abastecimento.csv")

    print(f"[INFO] Carregando veículos de: {path_veiculos}")
    veiculos = pd.read_csv(path_veiculos)[["fleet_number", "vehicle_type"]]
    veiculos = veiculos.rename(columns={"fleet_number": "vehicle_number"})

    print(f"[INFO] Carregando dados limpos de: {path_abastecimento}")
    abastecimento = pd.read_csv(path_abastecimento, sep=',')
    print(f"[INFO] Carregando dados inválidos de: {path_abastecimento_inv}")
    abastecimento_invalido = pd.read_csv(path_abastecimento_inv, sep=',')

    abastecimento          = abastecimento.merge(veiculos, on="vehicle_number", how="left")
    abastecimento_invalido = abastecimento_invalido.merge(veiculos, on="vehicle_number", how="left")

    clf = VoteEnsemble()
    # km_driven
    clf.fit(abastecimento["km_driven"])
    abastecimento["anomaly_km_driven"] = clf.predict(abastecimento["km_driven"])
    if not abastecimento_invalido.empty:
        abastecimento_invalido["anomaly_km_driven"] = clf.predict(abastecimento_invalido["km_driven"])

    # consumption
    clf.fit(abastecimento["consumption"])
    abastecimento["anomaly_consumption"] = clf.predict(abastecimento["consumption"])
    if not abastecimento_invalido.empty:
        abastecimento_invalido["anomaly_consumption"] = clf.predict(abastecimento_invalido["consumption"])

    # liter_supply
    clf.fit(abastecimento["liter_supply"])
    abastecimento["anomaly_liter_supply"] = clf.predict(abastecimento["liter_supply"])
    if not abastecimento_invalido.empty:
        abastecimento_invalido["anomaly_liter_supply"] = clf.predict(abastecimento_invalido["liter_supply"])

    # Combina e converte booleanos para 0/1
    abastecimento = pd.concat([abastecimento, abastecimento_invalido], ignore_index=True)
    abastecimento = abastecimento.replace({True: 1, False: 0})

    # Salva CSV de anomalias
    abastecimento.to_csv(path_saida, index=False)
    print(f"[INFO] CSV de anomalias salvo em: {path_saida}")
