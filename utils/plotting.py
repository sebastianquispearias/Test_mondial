# utils/plotting.py

import matplotlib.pyplot as plt
import seaborn as sns

def plot_boxplot_for_vehicle(df, vehicle_id, maintenance_result):
    """
    Genera un boxplot de NOx por la clasificación de velocidad para un vehículo,
    y añade en el título el resultado de la detección de mantenimiento.
    """
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    
    # Definición del orden de categorías
    order_categories = ['lenta', 'media', 'elevada']
    
    # Boxplot
    ax = sns.boxplot(data=df, x="clasificacion_velocidade", y="NOx", order=order_categories, dodge=True)
    # Puntos individuales (stripplot)
    sns.stripplot(data=df, x="clasificacion_velocidade", y="NOx", order=order_categories,
                  jitter=True, color=".3", size=5)
    
    # Determinar el mensaje según el resultado obtenido
    if maintenance_result.get('requiere_manutencao') is True:
        maint_text = "Requiere Mantenimiento"
    elif maintenance_result.get('requiere_manutencao') is False:
        maint_text = "No requiere Mantenimiento"
    else:
        maint_text = "Estado Indeterminado"
    
    plt.title(f"Vehículo {vehicle_id} - {maint_text}", fontsize=14)
    plt.xlabel("Clasificación de Velocidad", fontsize=12)
    plt.ylabel("Nivel de NOx", fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    filename = f"boxplot_vehicle_{vehicle_id}.png"
    plt.savefig(filename, bbox_inches="tight")
    plt.show()
    print(f"Boxplot individual guardado como '{filename}'")

def plot_global_boxplot(df):
    """
    Genera un boxplot global usando el DataFrame de todos los vehículos,
    donde en el eje X se muestre el 'vehicle_number' y se diferencie la clasificación
    de velocidad (hue = 'clasificacion_velocidade').
    """
    plt.figure(figsize=(14, 8))
    sns.set_style("whitegrid")
    
    ax = sns.boxplot(data=df, x="vehicle_number", y="NOx", hue="clasificacion_velocidade", dodge=True)
    plt.title("Distribución Global de NOx por Vehículo y Clasificación de Velocidad", fontsize=14)
    plt.xlabel("Número de Vehículo", fontsize=12)
    plt.ylabel("Nivel de NOx", fontsize=12)
    plt.xticks(rotation=90)
    plt.tight_layout()
    
    filename = "global_boxplot_nox.png"
    plt.savefig(filename, bbox_inches="tight")
    plt.show()
    print(f"Boxplot global guardado como '{filename}'")
