import pandas as pd

def export_maintenance_summary_csv(maintenance_results, output_filename="maintenance_summary.csv"):
    """
    Exporta un resumen de los resultados de mantenimiento a un archivo CSV.

    Cada fila contendrá:
      - Vehicle: número del vehículo.
      - Requiere Mantenimiento: True/False.
      - NOx Lenta: promedio ponderado para intervalos clasificados como "lenta".
      - NOx Media: promedio ponderado para intervalos clasificados como "media".
      - NOx Elevada: promedio ponderado para intervalos clasificados como "elevada".
    """
    summary_rows = []
    for result in maintenance_results:
        vehicle = result.get('vehicle_number')
        r = result.get('resultado_manutencao', {})
        resumo_nox = r.get('resumo_nox', {})
        requiere = r.get('requiere_manutencao')
        summary_row = {
            'Vehicle': vehicle,
            'Requiere Mantenimiento': requiere,
            'NOx Lenta': resumo_nox.get('lenta'),
            'NOx Media': resumo_nox.get('media'),
            'NOx Elevada': resumo_nox.get('elevada')
        }
        summary_rows.append(summary_row)
    # Crear DataFrame a partir de las filas de resumen
    df_summary = pd.DataFrame(summary_rows)
    df_summary.to_csv(output_filename, index=False)
    print(f"Archivo CSV '{output_filename}' generado con éxito.")

# Función opcional para exportar a Excel con resumen y detalles en hojas separadas:
def export_maintenance_results_excel(maintenance_results, output_filename="maintenance_results.xlsx"):
    """
    Exporta los resultados de mantenimiento a un archivo Excel.
    
    Crea:
      - Hoja "Resumen": un resumen de cada vehículo.
      - Una hoja por vehículo (por ejemplo, "Vehiculo_101") con los DataFrames de intervalos, si existen.
    """
    summary_rows = []
    details = {}  # Guardamos el DataFrame de intervalos para cada vehículo

    for result in maintenance_results:
        vehicle = result.get('vehicle_number')
        r = result.get('resultado_manutencao', {})
        resumo_nox = r.get('resumo_nox', {})
        requiere = r.get('requiere_manutencao')
        summary_row = {
            'Vehicle': vehicle,
            'Requiere Mantenimiento': requiere,
            'NOx Lenta': resumo_nox.get('lenta'),
            'NOx Media': resumo_nox.get('media'),
            'NOx Elevada': resumo_nox.get('elevada')
        }
        summary_rows.append(summary_row)
        if 'intervalos' in r and not r['intervalos'].empty:
            details[vehicle] = r['intervalos']
    
    df_summary = pd.DataFrame(summary_rows)
    
    with pd.ExcelWriter(output_filename) as writer:
        df_summary.to_excel(writer, sheet_name="Resumen", index=False)
        for vehicle, df_int in details.items():
            # Nombre de hoja (Excel acepta hasta 31 caracteres)
            sheet_name = f"Vehiculo_{vehicle}"
            if len(sheet_name) > 31:
                sheet_name = sheet_name[:31]
            df_int.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"Archivo Excel '{output_filename}' generado con éxito.")
