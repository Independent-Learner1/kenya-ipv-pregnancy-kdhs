"""Reusable choropleth tools for Kenya's 47 counties.

Use as a library:
    from choropleth import load_counties, static_choropleth, interactive_choropleth
    gdf = load_counties().merge(my_df, on="county")
    static_choropleth(gdf, "value", "My title", "map.png")

Or from the command line with any CSV that has a county name column and a value column:
    python src/choropleth.py --csv my.csv --county-col county --value-col rate \
        --title "My indicator (%)" --out outputs/maps/my_map
"""
import argparse
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from config import GEO, ORANGES, NAME_FIX

GEOJSON = GEO / "kenya_counties_geoBoundaries_ADM1.geojson"
CMAP = LinearSegmentedColormap.from_list("oranges_custom", ORANGES)


def load_counties():
    """Return a GeoDataFrame with a standard 'county' column (DHS spelling)."""
    g = gpd.read_file(GEOJSON)[["shapeName", "geometry"]].rename(columns={"shapeName": "county"})
    g["county"] = g["county"].replace({v: k for k, v in NAME_FIX.items()})
    return g


def static_choropleth(gdf, column, title, path, scheme="quantiles", k=5, cmap=CMAP,
                      legend_title=None, label_counties=False):
    fig, ax = plt.subplots(figsize=(7, 8))
    gdf.plot(column=column, cmap=cmap, scheme=scheme, k=k, edgecolor="white", linewidth=0.5, ax=ax,
             legend=True, legend_kwds={"title": legend_title or column, "loc": "lower left",
                                       "fmt": "{:.1f}", "frameon": False},
             missing_kwds={"color": "#e5e5e5", "label": "No data"})
    if label_counties:
        for _, r in gdf.iterrows():
            c = r.geometry.representative_point()
            ax.annotate(r["county"], (c.x, c.y), fontsize=4.5, ha="center")
    ax.set_title(title, fontsize=12, loc="left"); ax.axis("off")
    fig.text(0.01, 0.01, "Boundaries: geoBoundaries (CC BY 4.0). Data: KDHS 2022.", fontsize=6, color="#555")
    fig.savefig(path, dpi=200, bbox_inches="tight"); plt.close(fig)


def categorical_map(gdf, column, colors, title, path):
    fig, ax = plt.subplots(figsize=(7, 8))
    for cat, col in colors.items():
        s = gdf[gdf[column] == cat]
        if len(s):
            s.plot(color=col, edgecolor="white", linewidth=0.5, ax=ax, label=f"{cat} ({len(s)})")
    ax.legend(loc="lower left", frameon=False, fontsize=8)
    ax.set_title(title, fontsize=12, loc="left"); ax.axis("off")
    fig.savefig(path, dpi=200, bbox_inches="tight"); plt.close(fig)


def interactive_choropleth(gdf, column, title, path, tooltip_cols=None):
    import folium
    g = gdf.to_crs(4326)
    m = folium.Map(location=[0.2, 37.9], zoom_start=6, tiles="cartodbpositron")
    folium.Choropleth(geo_data=g.to_json(), data=g, columns=["county", column], key_on="feature.properties.county",
                      fill_color="Oranges", fill_opacity=0.85, line_opacity=0.4, nan_fill_color="#dddddd",
                      legend_name=title).add_to(m)
    cols = ["county"] + (tooltip_cols or [column])
    folium.GeoJson(g, style_function=lambda x: {"fillOpacity": 0, "weight": 0},
                   tooltip=folium.GeoJsonTooltip(fields=cols, aliases=cols, localize=True)).add_to(m)
    m.save(str(path))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True); ap.add_argument("--county-col", default="county")
    ap.add_argument("--value-col", required=True); ap.add_argument("--title", default="")
    ap.add_argument("--out", required=True, help="output path without extension")
    a = ap.parse_args()
    df = pd.read_csv(a.csv).rename(columns={a.county_col: "county"})
    df["county"] = df["county"].replace(NAME_FIX | {"Tharaka Nithi": "Tharaka-Nithi"})
    gdf = load_counties().merge(df[["county", a.value_col]], on="county", how="left")
    static_choropleth(gdf, a.value_col, a.title or a.value_col, a.out + ".png")
    interactive_choropleth(gdf, a.value_col, a.title or a.value_col, a.out + ".html")
    print("Wrote", a.out + ".png", "and", a.out + ".html")
