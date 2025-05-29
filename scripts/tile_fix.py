import pickle
import geopandas as gpd

# Load tile_index.pkl
with open("./tile_index.pkl", "rb") as f:
    gdf = pickle.load(f)

# Add WKT geometry column
gdf['geometry_wkt'] = gdf.geometry.to_wkt()

# Export to CSV
gdf[['name', 'geometry_wkt']].to_csv("./tile_index_wkt.csv", index=False)

print("Export complete: tile_index_wkt.csv")
