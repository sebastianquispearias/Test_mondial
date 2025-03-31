import math

def haversine(lat1, lon1, lat2, lon2):
    """
    Parâmetros:
      lat1, lon1: coordenadas do primeiro ponto (em graus decimais)
      lat2, lon2: coordenadas do segundo ponto (em graus decimais)
    
    Retorna:
      Distância em km. Em caso de erro na conversão dos valores, retorna 0.
    """
    try:
        lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
    except (ValueError, TypeError):
        return 0

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    R = 6371.0  # Raio da Terra em km
    return R * c

def obter_filial_con_estado(lat, lon, branches):
    """
    Dada una latitud y longitud, retorna el nombre de la filial si la distancia al punto
    de la filial es menor o igual al umbral especificado (por defecto 0.2 km).
    """
    for branch in branches:
        threshold = branch.get("umbral", 0.2)
        if haversine(lat, lon, branch['lat'], branch['lon']) <= threshold:
            return branch['name']  # Aquí se asume que el nombre de la filial se define en 'name'
    return ""

def extract_coordinates(df):
    """
    Extrae las coordenadas 'lon' y 'lat' de la columna 'position' en formato POINT(lon lat)
    y las añade al DataFrame.
    """
    df[['lon', 'lat']] = df['position'].str.extract(r'POINT\(([-\d\.]+) ([-\d\.]+)\)').astype(float)
    return df

def filtrar_gps(df: pd.DataFrame, lat_min: float, lat_max: float, lon_min: float, lon_max: float) -> pd.DataFrame:
    """
    Filtra filas del DataFrame:
      - Elimina aquellas con latitud y longitud iguales a 0.
      - Elimina las filas que tengan coordenadas fuera de los límites dados.
    """
    df = df.copy()
    # Filtrar filas con coordenadas 0,0
    df = df[~((df['lat'] == 0) & (df['lon'] == 0))]
    # Filtrar filas fuera del rango especificado
    df = df[(df['lat'] >= lat_min) & (df['lat'] <= lat_max) &
            (df['lon'] >= lon_min) & (df['lon'] <= lon_max)]
    return df