import sys
import os
import pandas as pd
from preprocess.ensemble import VoteEnsemble

# Define el path local donde se encuentran los datos
path = "./"  
sys.path.append(path)

# Verifica si las carpetas y archivos necesarios existen
if not os.path.exists(path + "dados limpos/"):
    os.makedirs(path + "dados limpos/")
if not os.path.exists(path + "anomalias/"):
    os.makedirs(path + "anomalias/")
if not os.path.exists(path + "dados limpos/invalidos/"):
    os.makedirs(path + "dados limpos/invalidos/")

nox_exists = os.path.exists(path + "dados limpos/nox.csv")
abastecimento_exists = os.path.exists(path + "dados limpos/abastecimentos.csv")
nox_invalidos_exists = os.path.exists(path + "dados limpos/invalidos/invalid_nox.csv")
abastecimento_invalidos_exists = os.path.exists(path + "dados limpos/invalidos/invalid_consumption.csv")


# Carga los datos si existen
if nox_exists and abastecimento_exists :
    nox = pd.read_csv(path + "dados limpos/nox.csv")
    veiculos = pd.read_csv(path + "dados/informacoes_veiculos.csv")
    abastecimento = pd.read_csv(path + "dados limpos/abastecimentos.csv")
    abastecimento_invalido = pd.read_csv(path + "dados limpos/invalidos/invalid_consumption.csv")
   
    # Agregar la columna `vehicle_type`
    veiculos = veiculos[["fleet_number", "vehicle_type"]].rename(columns={"fleet_number": "vehicle_number"})
    abastecimento = abastecimento.merge(veiculos, on="vehicle_number", how="left")
    abastecimento_invalido = abastecimento_invalido.merge(veiculos, on="vehicle_number", how="left")



    # Detecta anomalías en abastecimento (km_driven,consumption e liter_supply )
    clf = VoteEnsemble()

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

    #  Unir ambos .csv e salvar
    abastecimento = pd.concat([abastecimento, abastecimento_invalido], ignore_index=True)
    abastecimento = abastecimento.replace({True: 1, False: 0})
    abastecimento.to_csv(path + "anomalias/abastecimentos.csv", index=False)

# Detecta anomalías en nox
if nox_exists:
    clf = VoteEnsemble()
    nox["anomaly_nox"] = clf.fit_predict(nox["NOx"])
    nox["anomaly_o2"] = clf.fit_predict(nox["O2"])
    nox = nox.replace({True: 1, False: 0})
    nox.to_csv(path + "anomalias/nox.csv", index=False)

