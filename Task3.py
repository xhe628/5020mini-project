import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import numpy as np
from datetime import datetime
from matplotlib.colors import ListedColormap
import warnings
warnings.filterwarnings('ignore')
from scipy import stats

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
fire_df = pd.read_excel("/Users/camila/Desktop/CNGF5020/Project/output/火灾分类_总览.xlsx")
county_boundary = gpd.read_file("/Users/camila/Desktop/CNGF5020/Project/Mini Group Project I Data/CHN_County.shp")
county_boundary = county_boundary.to_crs("EPSG:4326")
heilongjiang_county = county_boundary[county_boundary["省级"] == "黑龙江省"].copy()
print(f"黑龙江省县级数量：{len(heilongjiang_county)}（正常）")

if "acq_date" in fire_df.columns:
    fire_df["acq_date"] = pd.to_datetime(fire_df["acq_date"])
    fire_df["year"] = fire_df["acq_date"].dt.year
fire_df_2010_2019 = fire_df[(fire_df["year"] >= 2010) & (fire_df["year"] <= 2019)].copy()
print(f"2010-2019年火灾总数据量：{len(fire_df_2010_2019)}（正常）")

fire_gdf = gpd.GeoDataFrame(
    fire_df_2010_2019,
    geometry=gpd.points_from_xy(fire_df_2010_2019["longitude"], fire_df_2010_2019["latitude"]),
    crs="EPSG:4326"
)
county_fire = gpd.sjoin(fire_gdf, heilongjiang_county, how="inner", predicate="within")
print(f"\n匹配到黑龙江省县级的火灾点数量：{len(county_fire)}（正常）")

county_fire.rename(columns={"year_left": "year"}, inplace=True)
if "year_right" in county_fire.columns:
    county_fire.drop(columns=["year_right"], inplace=True)

county_field = "县级"
if county_field not in county_fire.columns:
    raise ValueError(f"未找到县级字段'{county_field}'，请检查列名！")

fire_types = [
    "玉米秸秆焚烧",   
    "小麦秸秆焚烧",      
    "非农业火灾"       
]

trend_results = {}
#County-level Interannual Trend (2010-2019)
def trend_slope(series):
    if len(series) < 2:
        return np.nan
    x = np.arange(len(series))
    slope, _, _, _, _ = stats.linregress(x, series)
    return slope

for fire_type in fire_types:
    type_data = county_fire[county_fire["火灾类型"] == fire_type].copy()
    print(f"\n{fire_type}数据量：{len(type_data)}（正常）")
    
    if len(type_data) == 0:
        trend_results[fire_type] = pd.DataFrame({
            county_field: heilongjiang_county[county_field].unique(),
            "trend_slope": np.nan,
            "trend_type": np.nan
        })
        continue
    
    county_yearly = type_data.groupby([county_field, "year"]).size().reset_index(name="count")
    county_trend = county_yearly.groupby(county_field)["count"].apply(trend_slope).reset_index(name="trend_slope")
    county_trend["trend_type"] = pd.cut(
        county_trend["trend_slope"],
        bins=[-np.inf, -0.5, 0.5, np.inf],
        labels=["Significant Decrease", "Basically Stable", "Significant Increase"]
    )
    trend_results[fire_type] = county_trend


colors = ["#2ecc71", "#f39c12", "#e74c3c"]
labels = ["Significant Decrease", "Basically Stable", "Significant Increase"]
cmap = ListedColormap(colors)

fig, axes = plt.subplots(1, 3, figsize=(24, 10))

for i, fire_type in enumerate(fire_types):
    county_with_trend = heilongjiang_county.merge(
        trend_results[fire_type], 
        on=county_field, 
        how="left"
    )
    
    county_with_trend.plot(
        column="trend_type",
        ax=axes[i],
        cmap=cmap,  
        legend=True if len(county_with_trend.dropna(subset=["trend_type"])) > 0 else False,
        legend_kwds={"loc": "upper right", "labels": labels}, 
        missing_kwds={"color": "lightgray"},
        categorical=True 
    )
    
    if len(county_fire[county_fire["火灾类型"] == fire_type]) == 0:
        axes[i].set_title(f"Heilongjiang County-level {fire_type} Interannual Trend (2010-2019)\n(No Data for This Type)", fontsize=12)
    else:
        axes[i].set_title(f"Heilongjiang County-level {fire_type} Interannual Trend (2010-2019)", fontsize=14)
    axes[i].axis("off")

plt.tight_layout()
plt.savefig("Heilongjiang_County-level_Fire_Trend_Map.png", dpi=300, bbox_inches="tight")
plt.show()

print("\n=== 县级火灾趋势统计 ===")
for fire_type in fire_types:
    print(f"\n{fire_type}：")
    trend_data = trend_results[fire_type].dropna(subset=["trend_type"])
    if len(trend_data) == 0:
        print("  无有效趋势数据（名称不匹配或无记录）")
    else:
        print(trend_data["trend_type"].value_counts(dropna=False))

# Overall Trend
fig, axes = plt.subplots(1, 3, figsize=(24, 6))

for i, fire_type in enumerate(fire_types):
    type_data = county_fire[county_fire["火灾类型"] == fire_type]
    province_yearly = type_data.groupby("year").size().reset_index(name="total_count")
    
    axes[i].plot(
        province_yearly["year"], 
        province_yearly["total_count"], 
        marker="o", 
        linewidth=2, 
        color="#e74c3c", 
        label="Annual count"
    )
    
    if len(province_yearly) >= 2:
        x = province_yearly["year"]
        y = province_yearly["total_count"]
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        axes[i].plot(x, p(x), "--", color="#3498db", label=f"Slope={z[0]:.2f}")
    
    axes[i].set_title(f"Heilongjiang {fire_type} Overall Trend (2010-2019)", fontsize=12)
    axes[i].set_xlabel("Year")
    axes[i].set_ylabel("Count")
    axes[i].grid(alpha=0.3)
    axes[i].legend()
    axes[i].set_xticks(province_yearly["year"].unique())

plt.tight_layout()
plt.savefig("Heilongjiang_multi_type_fire_overall_trend.png", dpi=300, bbox_inches="tight")
plt.show()

