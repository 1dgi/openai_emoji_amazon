import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.wkt import loads as wkt_loads
import pickle

# === PATHS ===
TILE_INDEX_PKL = "/Users/jole/Documents/lidar_glyphs/tile_index.pkl"
EMOJI_GLYPHS_PKL = "/Users/jole/Documents/lidar_glyphs/output/emoji_glyphs.pkl"

# === LOAD DATA ===
tile_gdf = pd.read_pickle(TILE_INDEX_PKL)
glyphs = pickle.load(open(EMOJI_GLYPHS_PKL, "rb"))
glyph_df = pd.DataFrame(glyphs)

# === MERGE ===
merged_df = glyph_df.merge(tile_gdf[["name", "geometry"]], left_on="tile", right_on="name", how="left")
merged_df = gpd.GeoDataFrame(merged_df, geometry="geometry", crs="EPSG:31983")

# === IDENTIFY RAREST COHORTS ===
rarest_tiles = [
    "MDS_color_2122-214.laz", "MDS_color_2446-122.laz", "MDS_color_2446-123.laz", "MDS_color_2446-124.laz",
    "MDS_color_2446-233.laz", "MDS_color_3212-362.laz", "MDS_color_3214-131.laz", "MDS_color_3214-441.laz",
    "MDS_color_3234-431.laz", "MDS_color_3312-454.laz", "MDS_color_3312-462.laz", "MDS_color_3314-421.laz",
    "MDS_color_3322-111.laz", "MDS_color_3334-354.laz", "MDS_color_3336-122.laz", "MDS_color_3433-223.laz",
    "MDS_color_3433-354.laz", "MDS_color_3434-352.laz", "MDS_color_3441-424.laz", "MDS_color_3441-461.laz",
    "MDS_color_3443-212.laz", "MDS_color_3443-311.laz", "MDS_color_3446-334.laz", "MDS_color_3446-364.laz",
    "MDS_color_4312-114.laz", "MDS_color_4331-133.laz", "MDS_color_4435-321.laz", "MDS_color_4435-434.laz"
]
merged_df["is_rare"] = merged_df["tile"].isin(rarest_tiles)

# === PLOT ===
fig, ax = plt.subplots(figsize=(12, 10))
merged_df[~merged_df["is_rare"]].plot(ax=ax, color="lightgray", markersize=1, label="Neutral Tiles")
merged_df[merged_df["is_rare"]].plot(ax=ax, color="red", markersize=15, label="Man-Made Concern Cohorts", marker="x")

ax.set_title("🧭 Final Overlay: Rarest Emoji Cohorts (Man-Made Candidates) vs Neutral Grid", fontsize=14)
ax.set_xlabel("UTM Easting (EPSG:31983)")
ax.set_ylabel("UTM Northing (EPSG:31983)")
ax.legend()
plt.grid(True)

# === SAVE OUTPUT ===
plt.savefig("/Users/jole/Documents/lidar_glyphs/image3.png", dpi=300, bbox_inches="tight")
plt.show()
