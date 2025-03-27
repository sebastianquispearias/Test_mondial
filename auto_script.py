import asyncio
import time 
import sys

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import nbformat #Abrir e ler os notes
from nbconvert.preprocessors import ExecutePreprocessor #executa celulas de codigo dentro de um note
import os

def execute_notebook(notebook_path):
    print(f"Notebook em execução: {notebook_path}")
    start_time = time.time()  

    with open(notebook_path) as f:
        nb = nbformat.read(f, as_version=4)

    #Inicio do codigo
    ep = ExecutePreprocessor(timeout=-1)
    try:
        ep.preprocess(nb, {'metadata': {'path': os.path.dirname(notebook_path)}})
        execution_time = (time.time() - start_time) / 60  # Calcula o tempo em minutos
        print(f"Notebook finalizado: {notebook_path} (Tempo de execução: {execution_time:.2f} minutos)")
    except Exception as e:
        print(f"Erro ao executar o notebook '{notebook_path}': {str(e)}")

if __name__ == "__main__":
    notebooks_to_execute = [
        "0_download.ipynb",
        "1_limpeza.ipynb",
        "1_parado_andando.ipynb",
        "2_anomalias.ipynb",
        "2_vis_boxplot.ipynb",
        "2_vis_heatmap.ipynb",
        "upload.ipynb"
    ]

    for notebook in notebooks_to_execute:
        execute_notebook(notebook)