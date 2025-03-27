import asyncio
import time
import sys
import os
import subprocess


# TODO: Verificar esse check para windows... Não deve fazer sentido dentro do Docker
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def execute_script(python_file_path):
    print(f"Script em execução: {python_file_path}")
    start_time = time.time()

    try:
        # Execute pipeline (use absolute path for each file to avoid path errors)
        abs_script_path = os.path.join(os.path.dirname(__file__), python_file_path)
        subprocess.run(["python", abs_script_path], check=True)
        execution_time = (time.time() - start_time) / 60  # Calculate time in minutes
        print(f"Script finalizado: {python_file_path} (Tempo de execução: {execution_time:.2f} minutos)")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o script '{python_file_path}': {e}")

if __name__ == "__main__":
    scripts_to_execute = [
        "0_download.py",
        "1_limpeza.py",
        "1_parado_andando.py",
        "2_anomalias.py",
        "3_upload.py"
    ]
    for script in scripts_to_execute:
        execute_script(script)