import os
import sys
import time
import datetime

# TODO: Improve imports, use absolute path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(root_dir)

from api.auth import save_token
from api.alis import nox, fuel, vehicles

file_name = os.path.basename(__file__)

# TODO: Melhorar logs:
#   1) Reutilizar métodos e reduzir code duplication
#   2) Decidir EN ou PT
#   3) Adicionar timestamp para cada mensagem de log
def log_message(message):
    print(f"[{current_time_BR()}] - [{file_name}]: {message}")          

def log_error(message):
    print(f"[{current_time_BR()}] - [{file_name} - ERROR]: {message}")
    
def current_time_BR():
    local_time = time.localtime()                                       # Obtém o horário local em formato de segundos
    brasilia_time = time.localtime(time.mktime(local_time) - 3 * 3600)  # Ajusta o horário para Brasília (UTC -3)
    return time.strftime("%H:%M:%S", brasilia_time)                     # Formata a hora em HH:MM:SS

if __name__ == '__main__':
    path = './'

    # Set env vars
    start = os.getenv("START_DATE", "06/09/2024")
    finish = os.getenv("FINISH_DATE", "13/09/2024")

    # TODO: Utilizar variável para dividir execuções do pipeline em Nox x Abastecimento
    executeAbastecimento = os.getenv("EXECUTE_ABASTECIMENTO", "False").lower() == "true"
    executeNox = os.getenv("EXECUTE_NOX","False").lower() == "true"
    
    print(' --------------- Configuração ------------------ ')
    print('START_DATE ', start)
    print('FINISH_DATE ', finish)
    print('EXECUTE_ABASTECIMENTO ', executeAbastecimento)
    print('EXECUTE_NOX ', executeNox)
    print(' ----------------------------------------------- ')
    
    start = time.mktime(datetime.datetime.strptime(start, "%d/%m/%Y").timetuple()) * 1000
    finish = time.mktime(datetime.datetime.strptime(finish, "%d/%m/%Y").timetuple()) * 1000

    # Autenticação
    token = save_token("token")
    with open("token") as file:
        token = file.read() # TODO: Verificar se faz sentido manter

    # Verifica cache
    folder_exists = os.path.exists(path+"dados/")
    if not folder_exists:
        os.makedirs(path+"dados/")

    # Download dados
    if executeAbastecimento:
        vehicles_file = path + "dados/informacoes_veiculos.csv"
        log_message(f"Starting download for {vehicles_file}")
        vehicles(token, vehicles_file)

        nox_file = path + "dados/nox.csv"
        log_message(f"Starting download for {nox_file}")
        nox(token, nox_file, start=start, finish=finish)

        fuel_file = path + "dados/abastecimentos.csv"
        log_message(f"Starting download for {fuel_file}")
        fuel(token, fuel_file, start=start, finish=finish)