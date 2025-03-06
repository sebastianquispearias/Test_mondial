import os
import sys
import pandas as pd

# TODO: Improve imports, use absolute path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(root_dir)

from preprocess.ensemble import VoteEnsemble

file_name = os.path.basename(__file__)

def log_message(message):
    print(f"[{file_name}]: {message}")

def log_error(message):
    print(f"[{file_name} - ERROR]: {message}")

if __name__ == '__main__':
    path = './'

    # TODO: Melhorar nomes de dirs. Exemplo "dados limpos/" -> "dados-limpos" (evitar espaços)

    # TODO: Verificar melhorias no processo de criar / reutilizar diretorios de CSVs intermediários.
    #   Se formos rodar uma imagem Docker nova toda a vez, não faz sentindo verificar se os diretórios existem ou não
    if not os.path.exists(path + "dados limpos/"): os.makedirs(path + "dados limpos/")
    nox_exists = os.path.exists(path + "dados limpos/nox.csv")
    abastecimento_exists = os.path.exists(path + "dados limpos/abastecimentos.csv")

    executeAbastecimento = os.getenv("EXECUTE_ABASTECIMENTO", "False").lower() == "true"
    executeNox = os.getenv("EXECUTE_NOX","False").lower() == "true"

    veiculos = pd.read_csv(path + "dados/informacoes_veiculos.csv", index_col=[0])

    if executeNox and nox_exists:
        nox = pd.read_csv(path + "dados limpos/nox.csv", index_col=[0])
        log_message("Found CSV files for NOx in 'dados_limpos'. Creating dataframes for NOx...")

        clf = VoteEnsemble()
        nox["anomaly_nox"] = clf.fit_predict(nox["NOx"])
        nox["anomaly_o2"] = clf.fit_predict(nox["O2"])
        nox = nox.replace({True: 1, False: 0})
        if not os.path.exists(path + "anomalias/"): os.makedirs(path + "anomalias/")
        nox.to_csv(path + "anomalias/nox.csv")
        log_message('Printing DF nox:')
        print(nox)

    if executeAbastecimento and abastecimento_exists:
        abastecimento = pd.read_csv(path + "dados limpos/abastecimentos.csv", index_col=[0])
        log_message("Found CSV files for Abastecimento in 'dados_limpos'. Creating dataframes for Abastecimento...")

        clf = VoteEnsemble()
        abastecimento["anomaly_km_driven"] = clf.fit_predict(abastecimento["km_driven"])
        abastecimento["anomaly_consumption"] = clf.fit_predict(abastecimento["consumption"])
        abastecimento["anomaly_liter_supply"] = clf.fit_predict(abastecimento["liter_supply"])
        abastecimento = abastecimento.replace({True: 1, False: 0})
        if not os.path.exists(path + "anomalias/"): os.makedirs(path + "anomalias/")
        abastecimento.to_csv(path + "anomalias/abastecimentos.csv")
        log_message('Printing DF abastecimento:')
        print(abastecimento)

    if (not abastecimento_exists) and (not nox_exists):
        log_error("Files for NOx and Abastecimento not found in 'dados_limpos'.")






