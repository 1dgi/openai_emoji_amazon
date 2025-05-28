import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.wkt import loads as wkt_loads
import numpy as np

# === File paths ===
tile_index_path = "/Users/jole/Documents/lidar_glyphs/tile_index.csv"
output_path = "/Users/jole/Documents/lidar_glyphs/image5.png"

# === Load CSV and convert geometry ===
df = pd.read_csv(tile_index_path)
geometry = df["geometry"].apply(wkt_loads)
gdf = gpd.GeoDataFrame(df.drop(columns=["geometry"]), geometry=geometry, crs="EPSG:31983")

# Compute centroids
gdf["centroid_x"] = gdf.geometry.centroid.x
gdf["centroid_y"] = gdf.geometry.centroid.y

# Simulate FFGI-like plasma signal score
np.random.seed(42)
gdf["FFGI_score"] = np.random.normal(loc=7, scale=1.5, size=len(gdf))

# Filter for top 0.5% rare "constellation" tiles
threshold = gdf["FFGI_score"].quantile(0.995)
stars = gdf[gdf["FFGI_score"] >= threshold]

# === Plot ===
fig, ax = plt.subplots(figsize=(8, 12), facecolor="black")
ax.set_facecolor("black")

# Background tiles
gdf.plot(ax=ax, color="dimgray", edgecolor="gray", linewidth=0.05, alpha=0.3)

# Star tiles (constellations)
stars.plot(
    ax=ax,
    color="white",
    marker="*",
    markersize=100,
    label="Plasma Signal Stars",
    zorder=5,
)

# === Final touches ===
plt.title("🌌 Final Overlay: Plasma Field Candidates (Top 0.5% FFGI Scores)", fontsize=13, color="white")
plt.xlabel("UTM Easting (EPSG:31983)", color="white")
plt.ylabel("UTM Northing", color="white")
plt.xticks(color="white")
plt.yticks(color="white")
plt.legend(facecolor="black", edgecolor="white", labelcolor="white")
plt.axis("equal")
plt.tight_layout()

# Save + show
plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="black")
plt.show()
