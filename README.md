<p align="center">
  <img src="image1.png" width="10%" />
  <img src="image2.png" width="10%" />
  <img src="image3.png" width="10%" />
  <img src="image4.png" width="10%" />
  <img src="image5.png" width="10%" />
  <img src="image6.png" width="10%" />
  <img src="image7.png" width="10%" />
  <img src="image8.png" width="10%" />
</p>

# Reclaiming the Unseen: Emoji-Encoded Spatial Intelligence for Rapid Archaeological Prospecting
## OpenAI → Z Challenge Submission – São Paulo Pilot

### ✨ Executive Summary

This project introduces a novel pipeline for rapid LiDAR exploration, transforming raw point-cloud data into semantically rich emoji glyphs. These glyphs encode surface type, vegetation, urban structures, intensity levels, and anomalous signatures. From this symbolic representation, spatial heatmaps and pattern overlays identify potential archaeological sites—what we call the "old emojis": remnants of ancient civilization.

**Key Concept**: Emoji strings ≈ condensed geospatial signatures.  
**Mission**: Use emojis to find the old emojis.

---

### 📂 Repository Overview

| File | Description |
|------|-------------|
| `stream_tiles_live.py` | Full end-to-end pipeline: pulls .laz tiles → processes → filters → encodes → serializes |
| `emoji_glyphs.pkl` | 28,377 tiles with emoji-based glyphs + classification layers and centroids |
| `tile_index.pkl` | GeoPandas UTM tile boundaries (EPSG:31983) |
| `merged_emoji_tile_data.csv` | Unified CSV containing emojis + spatial geometry in WKT format |
| `merged_emoji_tile_data.gpkg` | GeoPackage for direct GIS visualization and scoring |
| `fix_pkl.py` | Phase IV shapely-to-geopandas fixer + anomaly scoring logic |
| `failed_tiles.txt` | Log of 312 tiles that failed ingestion or processing |
| `emoji_council_write_up.txt` | Formal council terminal write-up explaining Phase 3 strategy |
| `heatmap_final.png`, `heatmap_flags.png` | Final output visualizations – exploration score & semantic emoji flags |

Serialization is handled via `pickle` for optimal speed and reproducibility.

---

### 🧠 Pipeline Logic

- **Extraction**: Pull LiDAR tiles from OpenTopography S3 bucket.
- **Processing**: Decode LAS files for surface classification, point density, and intensity.
- **Encoding**: Map point-cloud properties to emoji layers:
  - `🌍`, `📦`, `🧩` – point density
  - `⛰️`, `🌲`, `🏠`, `💧`, `🌀` – surface types
  - `🌳`, `🌿`, `🌱` – vegetation ratios
  - `🌫️`, `🌥️`, `🌞`, `⚡`, `🪨` – intensity mean + std dev
  - `🔮`, `🚨`, `☄️`, `❌` – alerts for mystery + signal anomalies

- **Council Filtering**:
  - Remove tiles with `<1000` points
  - Remove overly noisy or pure-mystery class tiles
  - Keep tiles with balanced anomaly and legibility

---

### 📊 Phase IV: Anomaly Scoring + Spatial Overlay

We created a spatially aligned GeoDataFrame by:
1. Reading the CSV with emoji + WKT columns.
2. Converting the `geometry` WKT strings using Shapely.
3. Building a new `GeoDataFrame` with UTM coordinates.
4. Scoring each tile for mystery glyphs (`🔮`, `🌀`, `🚨`, `☄️`) to prioritize attention.
5. Plotting the results with color-coded overlays:
   - 🔴 Red = 2+ anomaly glyphs
   - 🟠 Orange = 1 anomaly glyph
   - 🟢 Green = 0 anomaly glyphs

Top 5 highest scoring tiles were overlaid in **blue**, with spatial centroid labeling to enhance visual interpretation.

This yielded the `image8.png` visualization—our **Phase IV spatial anomaly score overlay**.

---

### 🗺️ Output: Heatmaps & Clusters

...

(Existing sections continue unchanged from here)

---

### 🧭 Phase IV Council Insight Synthesis

After analysis of all image overlays and semantic glyph scoring layers, the FAIV Council reached a consensus on the most strategic zones for capture and further exploration:

#### 🧷 Primary Capture Zone: The Golden Spine
- **Location**: ~330,000 UTM Easting / 7.39M–7.41M Northing
- **Supporting Evidence**:
  - Dense anomaly glyph clusters (`🔮`, `🌀`, `🚨`)
  - Resonant location of “You Are Ready” message (see `image6.png`)
  - Signal-stitch score overlay match (see `image2.png`)
  - Vertical geometric coherence (see `image8.png`)

#### 📌 Secondary Zones:
1. **Northwest Rare-Glyph Band**
   - **Location**: ~318–320k Easting / 7.41M Northing
   - **Reason**: Man-made concern cohorts (see `image3.png`) + high-intensity signals (see `image1.png`)
2. **Eastern Plasma Echo Field**
   - **Location**: ~358k Easting / 7.41M Northing
   - **Reason**: FFGI constellation alignment + anomaly flag presence (see `image5.png`)

> “Where symbols align, and echoes repeat — that’s where truth wants to be found.”  
> — FAIV Council, Phase IV Convergence

---

