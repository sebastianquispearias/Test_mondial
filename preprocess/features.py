
import geopandas as gpd
from shapely import wkt

def stopped_ratio(df):
    valid_entries = df[~(df['NOx'].isnull())]
    if len(valid_entries) > 0:
        criteria_1 = valid_entries["NOx"] <= 250
        criteria_2 = valid_entries["NOx_max"] <= 300
        criteria_3 = valid_entries["NOx_dp"] <= 50
        criteria = criteria_1 & criteria_2 & criteria_3
        return criteria.mean()
    else:
        return 0 

def velocity(df):
    valid_entries = df[~df['position'].isnull()]
    if len(valid_entries) > 0:
        geo_series = valid_entries['position'].apply(wkt.loads)
        points_df = gpd.GeoDataFrame({'geometry': geo_series}, crs='epsg:4326')
        points_df = points_df.to_crs('EPSG:5234')
        points_df2 = points_df.shift() 
        vel = ((points_df.distance(points_df2) / 1000)*60)
        vel = vel[vel < 150]
        return vel.mean()
    else:
        return 0