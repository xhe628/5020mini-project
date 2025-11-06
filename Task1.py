import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
fire_df = pd.read_excel("/Users/camila/Desktop/CNGF5020/Project/output/火灾分类_总览.xlsx")
county_boundary = gpd.read_file("/Users/camila/Desktop/CNGF5020/Project/Mini Group Project I Data/CHN_County.shp")
county_boundary = county_boundary.to_crs("EPSG:4326")


fire_df["acq_date"] = pd.to_datetime(fire_df["acq_date"])
fire_df["year"] = fire_df["acq_date"].dt.year
fire_df["month"] = fire_df["acq_date"].dt.month
fire_df["week"] = fire_df["acq_date"].dt.isocalendar().week
fire_df["season"] = pd.cut(
    fire_df["month"],
    bins=[0, 2, 5, 8, 11, 12],  
    labels=["Winter", "Spring", "Summer", "Autumn", "Winter"], 
    right=True,  
    ordered=False
)

fire_df_hlj = fire_df[
    (fire_df["longitude"] >= 121) & (fire_df["longitude"] <= 135) &
    (fire_df["latitude"] >= 43) & (fire_df["latitude"] <= 53)
].copy()

bounds = county_boundary.bounds
county_boundary["center_lon"] = bounds[["minx", "maxx"]].mean(axis=1)
county_boundary["center_lat"] = bounds[["miny", "maxy"]].mean(axis=1)

heilongjiang_county = county_boundary[
    (county_boundary["center_lon"] >= 121) & (county_boundary["center_lon"] <= 135) &
    (county_boundary["center_lat"] >= 43) & (county_boundary["center_lat"] <= 53)
].copy()

# 1. Seasonality Analysis (Monthly + Seasonal)
plt.figure(figsize=(12, 5)) 

# Monthly Distribution
plt.subplot(1, 2, 1)
monthly_counts = fire_df_hlj.groupby("month").size()
monthly_counts.plot(kind="bar", color="#1f77b4")
plt.title("Monthly Distribution of Fires in Heilongjiang Province", fontsize=12)
plt.xlabel("Month")
plt.ylabel("Number of Fires")
plt.xticks(rotation=0)

# Seasonal Distribution
plt.subplot(1, 2, 2)
seasonal_counts = fire_df_hlj.groupby("season").size()
seasonal_counts.plot(kind="pie", autopct="%1.1f%%", colors=["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"])
plt.title("Seasonal Distribution of Fires in Heilongjiang Province", fontsize=12)
plt.ylabel("")
plt.tight_layout()
plt.savefig("fire_seasonal_distribution.png", dpi=300, bbox_inches="tight")
plt.show()
heilongjiang_county = county_boundary[county_boundary["省级"] == "黑龙江省"].copy()
heilongjiang_province = heilongjiang_county.unary_union


fire_gdf = gpd.GeoDataFrame(
    fire_df,
    geometry=gpd.points_from_xy(fire_df["longitude"], fire_df["latitude"]),
    crs="EPSG:4326"
)

fire_df_hlj = fire_gdf[fire_gdf.within(heilongjiang_province)].copy()
fire_df_hlj = fire_df_hlj.drop(columns="geometry").reset_index(drop=True)

# Fire geographical distribution in Heilongjiang
plt.figure(figsize=(10, 8))
heilongjiang_county.plot(
    ax=plt.gca(),
    color="lightgray",
    edgecolor="gray",
    linewidth=0.8
)

sns.scatterplot(
    data=fire_df_hlj,
    x="longitude", y="latitude",
    hue="火灾类型",
    palette={
        "玉米秸秆焚烧": "#ff6b6b",
        "小麦秸秆焚烧": "#9b59b6",
        "非农业火灾": "#4ecdc4",
        "混合作物焚烧": "#ffa500"
    },
    alpha=0.6, s=10
)

min_lon, min_lat, max_lon, max_lat = heilongjiang_province.bounds
plt.xlim(min_lon - 0.1, max_lon + 0.1)
plt.ylim(min_lat - 0.1, max_lat + 0.1)

plt.title("Geographic Distribution of Fires in Heilongjiang Province by Type", fontsize=12)
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid(alpha=0.3)
plt.legend(title="Fire Type")
plt.savefig("fire_geographic_distribution.png", dpi=300, bbox_inches="tight")
plt.show()


# County-level thermal density map of fires
fire_gdf_hlj = gpd.GeoDataFrame(
    fire_df_hlj,
    geometry=gpd.points_from_xy(fire_df_hlj["longitude"], fire_df_hlj["latitude"]),
    crs="EPSG:4326"
)

county_fire = gpd.sjoin(heilongjiang_county, fire_gdf_hlj, how="left", predicate="contains")
county_fire_count = county_fire.groupby("县级").size().reset_index(name="fire_count")
heilongjiang_county = heilongjiang_county.merge(county_fire_count, on="县级", how="left")
heilongjiang_county["fire_count"] = heilongjiang_county["fire_count"].fillna(0)

fig, ax = plt.subplots(1, 1, figsize=(12, 10))
heilongjiang_county.plot(
    column="fire_count",
    ax=ax,
    cmap="YlOrRd",
    legend=True,
    legend_kwds={"label": "Number of Fires"},
    edgecolor="gray",
    linewidth=0.5
)

ax.set_xlim(min_lon - 0.1, max_lon + 0.1)
ax.set_ylim(min_lat - 0.1, max_lat + 0.1)
ax.set_title("County-level Fire Density Heatmap in Heilongjiang Province", fontsize=14)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
plt.savefig("county_fire_density_heatmap.png", dpi=300, bbox_inches="tight")
plt.show()

# Hotspot Weeks Identification
weekly_counts = fire_df_hlj.groupby(["year", "week"]).size().reset_index(name="count")
avg_weekly = weekly_counts.groupby("week")["count"].mean().reset_index()

hotspot_threshold = avg_weekly["count"].quantile(0.9)
hotspot_weeks = avg_weekly[avg_weekly["count"] >= hotspot_threshold]

plt.figure(figsize=(12, 4))
plt.plot(avg_weekly["week"], avg_weekly["count"], color="#1f77b4", linewidth=1.5)
plt.scatter(
    hotspot_weeks["week"], hotspot_weeks["count"],
    color="red", s=50, label=f"Hotspot Weeks (≥{hotspot_threshold:.1f} fires)"
)
plt.title("Weekly Distribution and Hotspot Weeks of Fires in Heilongjiang Province", fontsize=12)
plt.xlabel("Week Number")
plt.ylabel("Average Number of Fires")
plt.grid(alpha=0.3)
plt.legend()
plt.xticks(range(0, 54, 4))
plt.savefig("fire_weekly_distribution.png", dpi=300, bbox_inches="tight")
plt.show()

print("Hotspot Weeks (Week Number - Average Fire Count):")
print(hotspot_weeks.sort_values("count", ascending=False))
