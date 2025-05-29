import pickle
import geopandas as gpd

# Load the original pickle
with open("/Users/jole/Documents/lidar_glyphs/tile_index.pkl", "rb") as f:
    gdf = pickle.load(f)

# Sanity check
print(f"Loaded {len(gdf)} tile geometries.")

# Export to CSV
gdf.to_csv("/Users/jole/Documents/lidar_glyphs/tile_index.csv", index=False)
print("✅ Exported to tile_index.csv successfully.")
