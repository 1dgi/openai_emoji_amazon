import pandas as pd
import geopandas as gpd
from shapely.wkt import loads as wkt_loads
import matplotlib.pyplot as plt

# Load the CSV
df = pd.read_csv("tile_index.csv")
df["geometry"] = df["geometry"].apply(wkt_loads)

# Use this bulletproof line to construct the GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:31983")

# Compute centroids
gdf["centroid"] = gdf.geometry.centroid
gdf["centroid_x"] = gdf.centroid.x
gdf["centroid_y"] = gdf.centroid.y

# Plot
centroids = gpd.GeoDataFrame(geometry=gpd.points_from_xy(gdf["centroid_x"], gdf["centroid_y"]), crs="EPSG:31983")

# Set message point coords
msg_point = gpd.GeoDataFrame(geometry=gpd.points_from_xy([321433.4], [7344585.7]), crs="EPSG:31983")

fig, ax = plt.subplots(figsize=(10, 12))
centroids.plot(ax=ax, color='lightgray', markersize=5)
msg_point.plot(ax=ax, color='gold', marker='*', markersize=200, label="🟡 'You Are Ready'")
plt.title("📍 Full Forest Map: Hidden Message Location")
plt.legend()
plt.axis("equal")
plt.tight_layout()
plt.show()
