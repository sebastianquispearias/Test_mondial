import os
import sys

# Ajusta path para importar pacote 'process'
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
))

from process.process_abastecimento import process_abastecimento
from process.process_nox          import process_nox

def main():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    raw  = os.path.join(base, 'dados limpos')
    anom = os.path.join(base, 'anomalias')

    # Garante que diretórios existam
    for d in (raw, anom, os.path.join(raw, 'invalidos')):
        os.makedirs(d, exist_ok=True)

    executeAbastecimento = os.getenv(
        "EXECUTE_ABASTECIMENTO", "False"
    ).lower() == "true"
    executeNox = os.getenv(
        "EXECUTE_NOX", "False"
    ).lower() == "true"

    executeAbastecimento = False
    executeNox = True

    if executeAbastecimento:
        process_abastecimento(base, raw, anom)
    if executeNox:
        process_nox(base, raw, anom)
    if not (executeAbastecimento or executeNox):
        print("[ERRO] Nenhum pipeline selecionado: defina EXECUTE_ABASTECIMENTO ou EXECUTE_NOX")

if __name__ == '__main__':
    main()
