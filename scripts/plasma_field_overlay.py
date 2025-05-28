import pickle
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

# === Load Data ===
emoji_path = "output/emoji_glyphs.pkl"
gdf_path = "tile_index.pkl"
OUTPUT_IMAGE = "plasma_field_overlay.png"

# Load emoji data
with open(emoji_path, "rb") as f:
    emoji_df = pickle.load(f)
emoji_df = pd.DataFrame(emoji_df)

# Load GeoDataFrame
gdf = pickle.load(open(gdf_path, "rb"))

# Add centroids if missing
if "centroid_x" not in gdf.columns or "centroid_y" not in gdf.columns:
    gdf["centroid"] = gdf.geometry.centroid
    gdf["centroid_x"] = gdf.centroid.x
    gdf["centroid_y"] = gdf.centroid.y

# Merge dataframes
merged = emoji_df.merge(gdf[["name", "geometry", "centroid_x", "centroid_y"]], left_on="tile", right_on="name")
merged = gpd.GeoDataFrame(merged, geometry="geometry", crs="EPSG:31983")

# === Define Plasma-Like FFGI Score ===
def score_tile(row):
    score = 0
    glyph = row["glyph"]

    if "🚨" in glyph: score += 2
    if "🧩" in glyph: score += 2
    if "❌" in glyph: score += 1
    if "⚡" in glyph and "🌀" in glyph: score += 1
    if int(row["centroid_x"]) % 10 == 0: score += 1
    if int(row["centroid_y"]) % 10 == 0: score += 1
    if "🏗️" in glyph or "🪨" in glyph: score += 1

    return score

merged["ffgi_score"] = merged.apply(score_tile, axis=1)

# Filter tiles with high score
threshold = 8
plasma_tiles = merged[merged["ffgi_score"] >= threshold]

# === Plot ===
fig, ax = plt.subplots(figsize=(12, 12))
gdf.plot(ax=ax, color="lightgrey", edgecolor="white", linewidth=0.2)

# Show plasma tiles with visible fill
plasma_tiles.plot(ax=ax, color="red", edgecolor="black", linewidth=0.5, alpha=0.9)

# Emoji annotation overlay
for _, row in plasma_tiles.iterrows():
    ax.text(row["centroid_x"], row["centroid_y"], "🧩", fontsize=9, ha='center', va='center')

# Final aesthetics
plt.title("🧲 Final Overlay: Plasma Field Candidates (FFGI Score ≥ 8)", fontsize=14)
plt.axis("off")
plt.savefig(OUTPUT_IMAGE, bbox_inches="tight", dpi=300)
plt.show()
