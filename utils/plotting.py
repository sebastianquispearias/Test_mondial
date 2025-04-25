# utils/plotting.py

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
def plot_boxplot_intervals_with_weighted_mean(intervalos, vehicle_id, resumo, requiere_mant, mostrar_puntos=False):
    """
    Genera un boxplot con stripplot para la distribución de nox_ponderada 
    por clasificación de velocidad (lenta, media, elevada).
    Además:
      - Dibuja, en rojo, una línea horizontal con el valor del promedio 
        ponderado para cada categoría y lo anota.
      - Muestra en el título si el vehículo requiere mantenimiento.
      - Se puede activar o desactivar la visualización de los puntos individuales.
    """
    plt.figure(figsize=(12, 5))
    sns.set_style("whitegrid")
    
    order_categories = ['lenta', 'media', 'elevada']
    
    # Submuestreo en caso de demasiados datos
    max_points = 1000  
    if len(intervalos) > max_points:
        intervalos_plot = intervalos.sample(n=max_points, random_state=42)
    else:
        intervalos_plot = intervalos

    ax = sns.boxplot(
        data=intervalos_plot,
        x="clasificacao",
        y="nox_ponderada",
        order=order_categories,
        palette="Blues", 
        width=0.6,
        showfliers=True
    )
    
    # Si se desea mostrar los puntos, se utiliza el stripplot.
    if mostrar_puntos:
        sns.stripplot(
            data=intervalos_plot,
            x="clasificacao",
            y="nox_ponderada",
            order=order_categories,
            jitter=True,
            alpha=0.3,
            color="black",
            size=2,
            marker="o",
            edgecolor="none"
        )
    
    for i, cat in enumerate(order_categories):
        if cat in resumo and pd.notna(resumo[cat]):
            weighted_mean = resumo[cat]
            # La línea horizontal se dibuja usando posiciones posicionales.
            ax.hlines(weighted_mean, i - 0.3, i + 0.3, colors='red', linestyles='--', linewidth=2)
            # Para mover el valor de texto un poco más a la derecha, se puede sumar un offset al valor x.
            ax.text(i + 0.1, weighted_mean, f"{weighted_mean:.2f}", color='red', ha='center',
                    va='bottom', fontweight='bold')
    
    maintenance_str = "Sí" if requiere_mant else "No"
    
    plt.title(
        f"Vehículo {vehicle_id} - Resumen de intervalos\n(Requere manutenção: {maintenance_str})\nPromedio NOX = Línea roja",
        # f"Vehículo {vehicle_id} - Resumen de intervalos\n(Requiere mantenimiento: {maintenance_str})\nPromedio ponderado = Línea roja",
        fontsize=13
    )
    plt.xlabel("Classificação de Velocidade (intervalos)", fontsize=12)
    #plt.ylabel("NOx", fontsize=12)
    #plt.ylabel("NOx ponderado", fontsize=12)
    plt.xticks(rotation=0)
    plt.tight_layout()
    
    filename = f"boxplot_intervals_vehicle_{vehicle_id}.png"
    plt.savefig(filename, bbox_inches="tight")
    plt.show()
    print(f"Boxplot de intervalos guardado como '{filename}'")

def gerar_histogramas_consumo(abastecimento, vehicle_number):
    # Copia los datos
    df = abastecimento.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['month_year'] = df['timestamp'].dt.strftime('%Y-%m')

    # Filtrar solo el vehículo seleccionado
    df_vehicle = df[df['vehicle_number'] == vehicle_number]

    # Orden cronológico
    meses_ordenados = sorted(df_vehicle['month_year'].unique())

    # Graficar histogramas solapados en un mismo gráfico
    plt.figure(figsize=(12, 7))

    for mes in meses_ordenados:
        sns.histplot(
            df_vehicle[df_vehicle['month_year'] == mes]['consumption'], 
            bins=10, kde=True, label=mes, alpha=0.4
        )

    plt.title(f'Comparación de Histogramas del Consumo por mes\nVehículo: {vehicle_number}', fontsize=16)
    plt.xlabel('Consumo (litros/km)', fontsize=14)
    plt.ylabel('Frecuencia', fontsize=14)
    plt.legend(title='Mes-Año')
    plt.grid(True)
    plt.tight_layout()
    plt.show()