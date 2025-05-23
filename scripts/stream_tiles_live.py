import os
import pandas as pd
import subprocess
import laspy
import numpy as np
import geopandas as gpd
import pickle
from shapely.geometry import shape

# Directory setup
tile_dir = "../temp_tile"
pkl_output_path = "../output/emoji_glyphs.pkl"
tile_index_path = "/Users/jole/Documents/lidar_glyphs/tile_index.pkl"
pickle_cache_dir = "../glyph_cache"
os.makedirs(tile_dir, exist_ok=True)
os.makedirs("../output", exist_ok=True)
os.makedirs(pickle_cache_dir, exist_ok=True)

def get_all_tile_names():
    print("\U0001f4e1 Listing all tiles from OpenTopography S3 bucket...")
    result = subprocess.run([
        "aws", "s3", "ls", "s3://pc-bulk/BR17_SaoPaulo/",
        "--endpoint-url", "https://opentopography.s3.sdsc.edu",
        "--no-sign-request"
    ], capture_output=True, text=True)

    return [
        line.strip().split()[-1]
        for line in result.stdout.splitlines()
        if line.strip().endswith(".laz")
    ]

def append_feature_to_index(path, new_feature):
    tile_name = new_feature["properties"]["name"]
    geometry = shape(new_feature["geometry"])

    new_row = gpd.GeoDataFrame(
        {"name": [tile_name]},
        geometry=[geometry],
        crs="EPSG:31983"
    )

    if os.path.exists(path):
        with open(path, "rb") as f:
            gdf = pickle.load(f)
    else:
        gdf = gpd.GeoDataFrame(columns=["name", "geometry"])
        gdf.set_geometry("geometry", inplace=True)
        gdf.set_crs("EPSG:31983", inplace=True)

    if tile_name not in gdf["name"].values:
        gdf = pd.concat([gdf, new_row], ignore_index=True)
        with open(path, "wb") as f:
            pickle.dump(gdf, f)
        print(f"🗺️  Added {tile_name} to tile_index.pkl")

def get_bounds_from_las(las):
    x = las.x
    y = las.y
    return {
        "xmin": round(float(np.min(x)), 2),
        "xmax": round(float(np.max(x)), 2),
        "ymin": round(float(np.min(y)), 2),
        "ymax": round(float(np.max(y)), 2),
        "centroid": [round(float(np.mean(x)), 2), round(float(np.mean(y)), 2)]
    }

def load_tile_index():
    if not os.path.exists(tile_index_path):
        print(f"⚠️ Tile index PKL not found at {tile_index_path}. Starting fresh.")
        return gpd.GeoDataFrame()

    with open(tile_index_path, "rb") as f:
        gdf = pickle.load(f)

    if "name" not in gdf.columns:
        raise ValueError("Expected 'name' column not found in tile index.")

    gdf["tile_name"] = gdf["name"].str.extract(r"(MDS_color_\d{4}-\d{3})")[0] + ".laz"
    gdf = gdf.dropna(subset=["tile_name"]).set_index("tile_name")

    return gdf

def laz_to_emoji(filepath, tile_index_gdf):
    try:
        las = laspy.read(filepath)
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return None

    total_points = len(las.xyz)
    classification = las.classification
    intensity = las.intensity

    class_ids, class_counts = np.unique(classification, return_counts=True)
    class_summary = dict(zip(map(int, class_ids), map(int, class_counts)))

    mean_intensity = float(np.mean(intensity))
    std_intensity = float(np.std(intensity))

    tile_name = os.path.basename(filepath)
    location_data = {}

    if tile_name in tile_index_gdf.index:
        row = tile_index_gdf.loc[tile_name]
        bounds = row.geometry.bounds
        location_data = {
            "utm_zone": "EPSG:31983",
            "bounding_box": {
                "xmin": round(bounds[0], 2),
                "xmax": round(bounds[2], 2),
                "ymin": round(bounds[1], 2),
                "ymax": round(bounds[3], 2)
            },
            "centroid": [round(row.geometry.centroid.x, 2), round(row.geometry.centroid.y, 2)]
        }
    else:
        print(f"📌 {tile_name} not in index — calculating from point cloud...")
        bounds = get_bounds_from_las(las)
        location_data = {
            "utm_zone": "EPSG:31983",
            "bounding_box": {
                "xmin": bounds["xmin"],
                "xmax": bounds["xmax"],
                "ymin": bounds["ymin"],
                "ymax": bounds["ymax"]
            },
            "centroid": bounds["centroid"]
        }

        new_feature = {
            "type": "Feature",
            "properties": {"name": tile_name},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [bounds["xmin"], bounds["ymin"]],
                    [bounds["xmax"], bounds["ymin"]],
                    [bounds["xmax"], bounds["ymax"]],
                    [bounds["xmin"], bounds["ymax"]],
                    [bounds["xmin"], bounds["ymin"]]
                ]]
            }
        }
        append_feature_to_index(tile_index_path, new_feature)

    layers = {
        "density": None,
        "surface": [],
        "vegetation": [],
        "urban": [],
        "intensity": [],
        "mystery": [],
        "alert": []
    }

    if total_points > 5_000_000:
        layers["density"] = "🌍"
    elif total_points > 1_000_000:
        layers["density"] = "📦"
    else:
        layers["density"] = "🧩"

    for c in class_summary:
        if c == 2:
            layers["surface"].append("⛰️")
        elif c == 5:
            layers["surface"].append("🌲")
        elif c == 6:
            layers["surface"].append("🏠")
        elif c == 9:
            layers["surface"].append("💧")
        elif c in (19, 20):
            layers["mystery"].append("🌀")
        else:
            layers["surface"].append("❔")

    veg = class_summary.get(5, 0)
    if veg > 0:
        ratio = veg / total_points
        if ratio > 0.8:
            layers["vegetation"] = ["🌳", "🌲", "🌿"]
        elif ratio > 0.5:
            layers["vegetation"] = ["🌲", "🌿"]
        elif ratio > 0.2:
            layers["vegetation"] = ["🌱"]

    buildings = class_summary.get(6, 0)
    if buildings > 0:
        ratio = buildings / total_points
        if ratio > 0.6:
            layers["urban"] = ["🏙️", "🏢"]
        elif ratio > 0.3:
            layers["urban"] = ["🏗️"]
        else:
            layers["urban"] = ["🏚️"]

    if mean_intensity < 20:
        layers["intensity"].append("🌫️")
    elif mean_intensity < 60:
        layers["intensity"].append("🌥️")
    else:
        layers["intensity"].append("🌞")

    if std_intensity > 25:
        layers["intensity"].append("⚡")
    elif std_intensity < 10:
        layers["intensity"].append("🪨")

    if class_summary.get(19, 0) + class_summary.get(20, 0) > 0.9 * total_points:
        layers["mystery"].append("🔮")

    if total_points > 5_000_000 and class_summary.get(19, 0) / total_points > 0.8:
        layers["alert"].append("🚨")
    if mean_intensity > 90:
        layers["alert"].append("☄️")
    if std_intensity > 40:
        layers["alert"].append("❌")

    all_emojis = [layers["density"]] + sum([
        v if isinstance(v, list) else [v] for k, v in layers.items() if k != "density"
    ], [])

    return {
        "tile": tile_name,
        "glyph": " ".join(all_emojis),
        "layers": layers,
        "point_count": total_points,
        "classification": class_summary,
        "intensity_mean": round(mean_intensity, 2),
        "intensity_std": round(std_intensity, 2),
        "location": location_data
    }

def passes_council_filters(summary):
    total = summary["point_count"]
    std = summary["intensity_std"]
    class_summary = summary["classification"]
    glyph = summary["glyph"]

    if total < 1000:
        return False
    if std < 5 or std > 80:
        return False
    if class_summary.get(19, 0) + class_summary.get(20, 0) > 0.9 * total:
        if all(g in glyph for g in ["🌀", "🔮"]):
            return False
    return True

def process_tile(tile_path, tile_index_gdf):
    """
    Processes a single .laz tile:
    - Converts it to an emoji glyph using `laz_to_emoji`
    - Applies Council filters
    - Returns the result if valid, otherwise None
    """
    result = laz_to_emoji(tile_path, tile_index_gdf)
    return result if result and passes_council_filters(result) else None

def load_existing_pickle():
    if not os.path.exists(pkl_output_path):
        return []
    with open(pkl_output_path, "rb") as f:
        return pickle.load(f)

def save_to_pickle(data):
    with open(pkl_output_path, "wb") as f:
        pickle.dump(data, f)


def load_existing_tiles():
    if not os.path.exists(pkl_output_path):
        return {}, []

    if os.path.exists(pkl_output_path):
        glyph_list = load_existing_pickle()

    tile_map = {entry["tile"]: entry for entry in glyph_list}
    return tile_map, glyph_list

def main():
    processed_map, glyph_list = load_existing_tiles()
    tile_index_gdf = load_tile_index()
    all_tiles = get_all_tile_names()

    for tile_name in all_tiles:
        if tile_name in processed_map:
            print(f"⏭️  Skipping {tile_name} (already processed)")
            continue

        print(f"\n⬇️  Fetching {tile_name}...")
        local_path = os.path.join(tile_dir, tile_name)

        try:
            subprocess.run([
                "aws", "s3", "cp",
                f"s3://pc-bulk/BR17_SaoPaulo/{tile_name}", local_path,
                "--endpoint-url", "https://opentopography.s3.sdsc.edu",
                "--no-sign-request"
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to fetch {tile_name}: {e}")
            with open("../output/failed_tiles.txt", "a") as fail_log:
                fail_log.write(tile_name + "\n")
            continue

        print(f"🧠 Processing {tile_name}...")
        glyph = process_tile(local_path, tile_index_gdf)
        if glyph:
            glyph_list.append(glyph)
            save_to_pickle(glyph_list)
            print(f"💾 Saved emoji glyph for {tile_name} to PKL")
        else:
            print(f"⚠️ Skipped {tile_name} due to Council filtering.")

        os.remove(local_path)
        print(f"🧹 Removed {tile_name}")

    print(f"\n✅ All complete. Full output in {pkl_output_path}")

if __name__ == "__main__":
    main()
