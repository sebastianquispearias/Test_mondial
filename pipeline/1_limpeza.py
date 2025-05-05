import os
import sys
import pandas as pd

# TODO: Improve imports, use absolute path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(root_dir)

from preprocess.cleanup import filter_consumption, filter_odometer, filter_km
from preprocess.cleanup import filter_o2, filter_nox_avg, filter_nox_max, filter_nox_min, filter_nox_std
from preprocess.cleanup import filter_nox_duplicates
from preprocess.cleanup import filter_desligado, filter_coordinate_in_brazil

# TODO: Add logs

def full_csv(select = 'abastecimento'):
    nox_exists = os.path.exists(path+"dados/nox.csv")
    abastecimento_exists = os.path.exists(path+"dados/abastecimento.csv")
    if select == 'nox' and nox_exists:
        return pd.read_csv(path+'dados/nox.csv', sep=',')
    elif select == 'abastecimento' and abastecimento_exists:
        return pd.read_csv(path+'dados/abastecimento.csv', sep=';')

if __name__ == '__main__':
    path='./'

    executeAbastecimento = os.getenv("EXECUTE_ABASTECIMENTO", "False").lower() == "true"
    executeNox = os.getenv("EXECUTE_NOX","False").lower() == "true"
    
    executeAbastecimento = True############debug
    executeNox = True #####################
    # Cria, caso não exista, a pasta que armazenará os logs
    if not os.path.exists(path+"dados limpos/"): os.makedirs(path+"dados limpos/")
    nox_exists = os.path.exists(path+"dados/nox.csv")
    file_path = path + "dados/nox.csv"
    if nox_exists:
        print(f"Archivo {file_path} encontrado, tamaño: {os.path.getsize(file_path)} bytes")
    else:
        print(f"ERROR: Archivo {file_path} no encontrado")
    abastecimento_exists = os.path.exists(path+"dados/abastecimento.csv")

    # Limpeza - Abastecimento
    if executeAbastecimento:
        abastecimento = pd.read_csv(path+'dados/abastecimento.csv', index_col=[0], sep=';')
        old_size = len(abastecimento)
        abastecimento = filter_km(abastecimento, arg_return=0)
        print(len(abastecimento))
        abastecimento = filter_consumption(abastecimento, arg_return=0)
        print(len(abastecimento))
        abastecimento = filter_odometer(abastecimento, arg_return=0)
        print(len(abastecimento))
        abastecimento.to_csv(path+'dados limpos/abastecimento.csv')
        new_size = len(abastecimento)

    # Limpeza - NOx
    if executeNox:
        nox = pd.read_csv(path+'dados/nox.csv', index_col=[0], sep=',')
        print(f"DataFrame de NOx: {nox.shape[0]} filas")

        old_size = len(nox)
        nox = filter_o2(nox, arg_return=0)
        print(len(nox))
        nox = filter_nox_avg(nox, arg_return=0)
        print(len(nox))
        nox = filter_nox_max(nox, arg_return=0)
        print(len(nox))
        nox = filter_nox_min(nox, arg_return=0)
        print(len(nox))
        nox = filter_nox_std(nox, arg_return=0)
        print(len(nox))
        nox = filter_nox_duplicates(nox, arg_return=0)
        print(len(nox))
        # nox = filter_coordinate_duplicates(nox, arg_return=0)
        print(len(nox))
        nox = filter_desligado(nox, arg_return=0)
        print(len(nox))
        nox = filter_coordinate_in_brazil(nox, arg_return=0)
        print(len(nox))
        nox.to_csv(path+'dados limpos/nox.csv')
        print(f"Arquivo dados limpos/nox.csv gerado com sucesso")
        new_size = len(nox)

    # Aplicando regras de limpeza
    if not os.path.exists(path+'dados limpos/invalidos/'): os.makedirs(path+'dados limpos/invalidos/')
    if executeAbastecimento:
        filter_km(full_csv('abastecimento'), arg_return=1).to_csv(path+"dados limpos/invalidos/invalid_km.csv", index=False)
        filter_odometer(full_csv('abastecimento'), arg_return=1).to_csv(path+"dados limpos/invalidos/inverted_odometer.csv", index=False)
        filter_consumption(full_csv('abastecimento'), arg_return=1).to_csv(path+"dados limpos/invalidos/invalid_consumption.csv", index=False)

    if executeNox:
        filter_o2(full_csv('nox'), arg_return=1).to_csv(path+"dados limpos/invalidos/invalid_o2.csv", index=False)
        filter_nox_avg(full_csv('nox'), arg_return=1).to_csv(path+"dados limpos/invalidos/invalid_nox.csv", index=False)
        filter_desligado(full_csv('nox'), arg_return=1).to_csv(path+"dados limpos/invalidos/vehicle_off.csv", index=False)
        filter_nox_max(full_csv('nox'), arg_return=1).to_csv(path+"dados limpos/invalidos/invalid_nox_max.csv", index=False)
        filter_nox_min(full_csv('nox'), arg_return=1).to_csv(path+"dados limpos/invalidos/invalid_nox_min.csv", index=False)
        filter_nox_std(full_csv('nox'), arg_return=1).to_csv(path+"dados limpos/invalidos/invalid_nox_std.csv", index=False)
        filter_nox_duplicates(full_csv('nox'), arg_return=1).to_csv(path+"dados limpos/invalidos/nox_duplicates.csv", index=False)
        filter_coordinate_in_brazil(full_csv('nox'), arg_return=1).to_csv(path+"dados limpos/invalidos/outside_brazil.csv", index=False)
