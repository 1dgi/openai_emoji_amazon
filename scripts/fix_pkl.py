import pandas as pd
import geopandas as gpd
from shapely import wkt
from shapely.geometry import Polygon

# Step 1: Load CSV
raw_df = pd.read_csv("../output/merged_emoji_tile_data.csv")

# Step 2: Convert 'geometry' column to WKT safely
raw_df["geometry"] = raw_df["geometry"].apply(wkt.loads)

# Step 3: Manually build GeoSeries from the WKT-converted geometry
geometry_series = gpd.GeoSeries(raw_df["geometry"], crs="EPSG:31983")

# Step 4: Create GeoDataFrame manually
gdf = gpd.GeoDataFrame(raw_df.drop(columns=["geometry"]), geometry=geometry_series)

# Step 5: Score anomalies
gdf["score"] = gdf["glyph"].apply(lambda g: g.count("🔮") + g.count("🌀") + g.count("🚨") + g.count("☄️"))
gdf["color"] = gdf["score"].apply(lambda s: "red" if s >= 2 else ("orange" if s == 1 else "green"))

# Step 6: Plot
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(14, 12))
gdf.plot(ax=ax, color=gdf["color"], edgecolor='black', alpha=0.6)

# Highlight Top 5
top5 = gdf.sort_values("score", ascending=False).head(5)
top5.plot(ax=ax, color="blue", edgecolor="black")

for idx, row in top5.iterrows():
    c = row.geometry.centroid
    ax.annotate("Top", (c.x, c.y), color="blue", fontsize=10, weight="bold")

plt.title("Phase IV: Verified Anomalous Glyphs Across Forest Topology", fontsize=16)
plt.xlabel("UTM Easting")
plt.ylabel("UTM Northing")
plt.grid(True)
plt.tight_layout()
plt.show()
