## 一、核心库导入与编码配置（解决中文路径问题）
import os
import glob  # 新增：用于遍历文件夹中的CSV文件

# 1. 强制GDAL编码与路径配置（解决Windows中文编码冲突）
os.environ['GDAL_ENCODING'] = 'CP936'
os.environ['GDAL_DATA'] = r"D:\python\Lib\site-packages\osgeo\data\gdal"  # 你的GDAL_DATA路径
os.environ['PROJ_LIB'] = r"D:\python\Lib\site-packages\pyproj\proj_dir\share\proj"  # 你的PROJ路径
os.environ['GDAL_NO_GEOTIFF_OVR'] = 'YES'
os.environ['GDAL_DISABLE_READDIR_ON_OPEN'] = 'EMPTY_DIR'



# 2. 导入其他核心库
import pandas as pd
import numpy as np
import rasterio
from rasterio.transform import rowcol
import geopandas as gpd
from pyproj import Transformer
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import warnings

warnings.filterwarnings('ignore')

# 编码配置验证
print("=== 编码配置验证 ===")
print("GDAL_ENCODING：", os.getenv('GDAL_ENCODING'))
print("GDAL_DATA：", os.getenv('GDAL_DATA'))
print("PROJ_LIB：", os.getenv('PROJ_LIB'))
print("=== 验证结束 ===")

## 二、参数配置（适配文件夹读取）
# --------------------------  用户确认：路径与参数  --------------------------
# 1. 基础数据路径（修改为MODIS CSV文件夹路径）
MODIS_FOLDER = r"D:\AAA1assignment\Mini Group Project I Data\Satellite Fire Data"  # 存放所有MODIS CSV的文件夹
COUNTY_SHP = r"D:\AAA1assignment\Mini Group Project I Data\CHN_County.shp"
FY_CSV = r"D:\AAA1assignment\Mini Group Project I Data\straw burning fire point monitoring data.xlsx"

# 2. 作物栅格路径（玉米/小麦2010-2019年，与火点年份对应）
corn_raster_paths = {
    2010: r"D:\AAA1assignment\Mini Group Project I Data\Cropland distribution and phenological data\Heilongjiang_Maize_MA_2010.tif",
    2011: r"D:\AAA1assignment\Mini Group Project I Data\Cropland distribution and phenological data\Heilongjiang_Maize_MA_2011.tif",
    2012: r"D:\AAA1assignment\Mini Group Project I Data\Cropland distribution and phenological data\Heilongjiang_Maize_MA_2012.tif",
    2013: r"D:\AAA1assignment\Mini Group Project I Data\Cropland distribution and phenological data\Heilongjiang_Maize_MA_2013.tif",
    2014: r"D:\AAA1assignment\Mini Group Project I Data\Cropland distribution and phenological data\Heilongjiang_Maize_MA_2014.tif",
    2015: r"D:\AAA1assignment\Mini Group Project I Data\Cropland distribution and phenological data\Heilongjiang_Maize_MA_2015.tif",
    2016: r"D:\AAA1assignment\Mini Group Project I Data\Cropland distribution and phenological data\Heilongjiang_Maize_MA_2016.tif",
    2017: r"D:\AAA1assignment\Mini Group Project I Data\Cropland distribution and phenological data\Heilongjiang_Maize_MA_2017.tif",
    2018: r"D:\AAA1assignment\Mini Group Project I Data\Cropland distribution and phenological data\Heilongjiang_Maize_MA_2018.tif",
    2019: r"D:\AAA1assignment\Mini Group Project I Data\Cropland distribution and phenological data\Heilongjiang_Maize_MA_2019.tif"
}
wheat_raster_paths = {
    2010: r"D:\AAA1assignment\Mini Group Project I Data\Cropland distribution and phenological data\Heilongjiang_Wheat_MA_2010.tif",
    2011: r"D:\AAA1assignment\Mini Group Project I Data\Cropland distribution and phenological data\Heilongjiang_Wheat_MA_2011.tif",
    2012: r"D:\AAA1assignment\Mini Group Project I Data\Cropland distribution and phenological data\Heilongjiang_Wheat_MA_2012.tif",
    2013: r"D:\AAA1assignment\Mini Group Project I Data\Cropland distribution and phenological data\Heilongjiang_Wheat_MA_2013.tif",
    2014: r"D:\AAA1assignment\Mini Group Project I Data\Cropland distribution and phenological data\Heilongjiang_Wheat_MA_2014.tif",
    2015: r"D:\AAA1assignment\Mini Group Project I Data\Cropland distribution and phenological data\Heilongjiang_Wheat_MA_2015.tif",
    2016: r"D:\AAA1assignment\Mini Group Project I Data\Cropland distribution and phenological data\Heilongjiang_Wheat_MA_2016.tif",
    2017: r"D:\AAA1assignment\Mini Group Project I Data\Cropland distribution and phenological data\Heilongjiang_Wheat_MA_2017.tif",
    2018: r"D:\AAA1assignment\Mini Group Project I Data\Cropland distribution and phenological data\Heilongjiang_Wheat_MA_2018.tif",
    2019: r"D:\AAA1assignment\Mini Group Project I Data\Cropland distribution and phenological data\Heilongjiang_Wheat_MA_2019.tif"
}

# 3. 关键参数：分作物定义无效值与合理DOY范围（适配多年数据）
CROP_CONFIG = {
    "玉米": {
        "nodata": [65536, -3.4028234663852886e+38],  # 玉米无效值（异常值+NoData）
        "valid_doy": (200, 320)  # 黑龙江玉米成熟季（8-11月）
    },
    "小麦": {
        "nodata": [-3.4028234663852886e+38],  # 小麦无效值（NoData）
        "valid_doy": (150, 250)  # 黑龙江春小麦成熟季（5-8月）
    }
}
WINDOW_DAYS = 20  # 收获后燃烧窗口期（天）
FRP_MIN = 10  # 最小FRP
FRP_MAX = 5000  # 最大FRP
ANALYSIS_YEARS = range(2010, 2020)  # 明确分析2010-2019年
OUTPUT_DIR = r"C:\Users\毛毛\Desktop\研究牲\作业\CNGF5020\Mini Group Project I Data\Output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
# 按年份创建输出子目录，避免文件混乱
for year in ANALYSIS_YEARS:
    os.makedirs(os.path.join(OUTPUT_DIR, str(year)), exist_ok=True)


## 三、工具函数定义（保持不变）
def crs_transform(lon, lat, src_crs="EPSG:4326", dst_crs="EPSG:32651"):
    """坐标转换：WGS84→目标CRS（适配所有年份栅格）"""
    transformer = Transformer.from_crs(src_crs, dst_crs, always_xy=True)
    x, y = transformer.transform(lon, lat)
    return x, y


def get_crop_maturity(fire_x, fire_y, crop_type, year, crop_raster_paths, debug=False):
    """提取火点位置的作物成熟DOY（按火点年份匹配对应栅格）"""
    crop_cfg = CROP_CONFIG[crop_type]
    raster_path = crop_raster_paths.get(year, None)  # 用当前火点的年份读取对应栅格

    # 1. 检查栅格路径有效性（按年份）
    if not raster_path or not os.path.exists(raster_path):
        if debug:
            print(f"警告：{crop_type}{year}年栅格不存在 → {raster_path}")
        return None

    try:
        with rasterio.open(raster_path) as src:
            row, col = rowcol(src.transform, fire_x, fire_y)
            # 2. 检查行列号是否在栅格范围内
            if not (0 <= row < src.height and 0 <= col < src.width):
                if debug:
                    print(f"{crop_type}{year}年栅格：火点行列号({row},{col})超出范围({src.height},{src.width})")
                return None

            # 3. 读取原始值并过滤无效值（分作物）
            raw_doy = src.read(1)[row, col]
            if debug:
                print(f"{crop_type}{year}年栅格：原始DOY={raw_doy}")

            # 3.1 排除无效值（含NoData和异常值）
            if any(np.isclose(raw_doy, nd, atol=1e-30) for nd in crop_cfg["nodata"]):
                if debug:
                    print(f"{crop_type}{year}年栅格：无效值（{raw_doy}）已过滤")
                return None

            # 3.2 排除超出合理范围的DOY（按作物物候）
            if not (crop_cfg["valid_doy"][0] <= raw_doy <= crop_cfg["valid_doy"][1]):
                if debug:
                    print(f"{crop_type}{year}年栅格：DOY={raw_doy}超出合理范围{crop_cfg['valid_doy']}")
                return None

            # 4. 返回有效DOY（整数）
            return int(raw_doy)
    except Exception as e:
        if debug:
            print(f"读取{crop_type}{year}年栅格错误 → {str(e)}")
        return None


def is_in_window(fire_doy, crop_maturity_doy, window_days=20):
    """判断火点是否在作物成熟后的窗口期内（适配所有年份）"""
    if pd.isna(crop_maturity_doy):
        return False
    window_start = crop_maturity_doy + 1
    window_end = crop_maturity_doy + window_days

    # 处理跨年情况（如12月成熟，窗口期跨到次年1月）
    if window_end > 365:
        return (fire_doy >= window_start) or (fire_doy <= (window_end - 365))
    else:
        return window_start <= fire_doy <= window_end


def classify_fire(row):
    """火灾分类（适配多年数据，基于有效DOY）"""
    corn_cond = pd.notna(row["玉米成熟DOY"]) and row["玉米窗口期内"]
    wheat_cond = pd.notna(row["小麦成熟DOY"]) and row["小麦窗口期内"]

    # 抽样打印（每5000个火点，按年份区分）
    if row.name % 5000 == 0 and (corn_cond or wheat_cond):
        print(f"火点ID={row.name}（{row['year']}年）：玉米关联={corn_cond}，小麦关联={wheat_cond}")

    if corn_cond and wheat_cond:
        return "混合作物焚烧"
    elif corn_cond:
        return "玉米秸秆焚烧"
    elif wheat_cond:
        return "小麦秸秆焚烧"
    else:
        return "非农业火灾"


## 四、主流程：2010-2019年多年数据处理（核心修改数据加载部分）
### 步骤1：加载MODIS火点数据（从文件夹读取所有CSV，2010-2019年中国范围）
print("\n=== 步骤1：从文件夹读取所有MODIS火点CSV（2010-2019年）并筛选黑龙江省 ===")

# 核心修改：遍历文件夹，获取所有CSV文件路径
if not os.path.exists(MODIS_FOLDER):
    raise FileNotFoundError(f"MODIS文件夹不存在 → {MODIS_FOLDER}")

# 使用glob查找文件夹中所有.csv文件（支持子文件夹）
csv_files = glob.glob(os.path.join(MODIS_FOLDER, "**", "*.csv"), recursive=True)
if not csv_files:
    raise FileNotFoundError(f"MODIS文件夹中未找到任何CSV文件 → {MODIS_FOLDER}")

print(f"找到{len(csv_files)}个MODIS CSV文件，开始合并...")
print("文件列表：")
for i, f in enumerate(csv_files, 1):
    print(f"  {i}. {os.path.basename(f)}")

# 读取并合并所有CSV文件（处理可能的编码和列名差异）
modis_dfs = []
required_cols = ["longitude", "latitude", "acq_date", "frp"]  # 必要字段

for file in csv_files:
    try:
        # 尝试不同编码读取（解决中文/特殊字符问题）
        try:
            df = pd.read_csv(file, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(file, encoding="gbk")

        # 检查必要字段（忽略大小写和空格）
        df_cols = [col.strip().lower() for col in df.columns]
        required_lower = [col.lower() for col in required_cols]
        missing = [req for req in required_lower if req not in df_cols]

        if missing:
            print(f"  跳过文件{os.path.basename(file)}：缺少字段{missing}")
            continue

        # 统一列名（映射到标准字段）
        col_mapping = {df.columns[i].strip(): req for i, req in enumerate(required_lower) if df_cols[i] == req}
        df = df.rename(columns=col_mapping)[required_cols].dropna()
        modis_dfs.append(df)
        print(f"  成功读取{os.path.basename(file)}：{len(df)}条记录")

    except Exception as e:
        print(f"  读取文件{os.path.basename(file)}失败：{str(e)}")
        continue

# 合并所有有效数据
if not modis_dfs:
    raise ValueError("没有有效CSV文件可合并，请检查文件格式和字段")
modis_df = pd.concat(modis_dfs, ignore_index=True)
print(f"合并后总火点数量：{len(modis_df)}条（原始数据）")

# 时间格式处理（提取年份和DOY，适配2010-2019）
modis_df["acq_date"] = pd.to_datetime(
    modis_df["acq_date"], format="%Y-%m-%d", errors="coerce"
).dropna()
modis_df["year"] = modis_df["acq_date"].dt.year  # 明确年份字段为"year"
modis_df["doy"] = modis_df["acq_date"].dt.dayofyear

# 筛选2010-2019年数据
modis_df = modis_df[modis_df["year"].isin(ANALYSIS_YEARS)]
modis_df = modis_df[(modis_df["frp"] >= FRP_MIN) & (modis_df["frp"] <= FRP_MAX)]
print(f"筛选后（2010-2019年，FRP在{FRP_MIN}-{FRP_MAX}）火点数量：{len(modis_df)}")

# 按年份统计原始火点数量
yearly_counts = modis_df["year"].value_counts().sort_index()
print("各年份原始火点数量：")
for year, cnt in yearly_counts.items():
    print(f"  {year}年：{cnt}个")

# 空间筛选：黑龙江省县级边界
if not os.path.exists(COUNTY_SHP):
    raise FileNotFoundError(f"县级矢量文件不存在 → {COUNTY_SHP}")
county_gdf = gpd.read_file(COUNTY_SHP).to_crs("EPSG:4326")
hlj_county = county_gdf[county_gdf["省级"].str.contains("黑龙江省", na=False)]
if len(hlj_county) == 0:
    raise ValueError("未找到黑龙江省县级数据！请检查矢量'省级'字段值")

# 火点空间连接（保留年份信息）
modis_gdf = gpd.GeoDataFrame(
    modis_df,
    geometry=gpd.points_from_xy(modis_df["longitude"], modis_df["latitude"]),
    crs="EPSG:4326"
)
hlj_fires = gpd.sjoin(modis_gdf, hlj_county, how="inner", predicate="within")
hlj_fires = hlj_fires.drop_duplicates(subset=["longitude", "latitude", "acq_date"])  # 去重
print(f"\n黑龙江省火点总数量（2010-2019年）：{len(hlj_fires)}")

# 按年份统计黑龙江火点数量
hlj_yearly_counts = hlj_fires["year_left"].value_counts().sort_index()
print("黑龙江省各年份火点数量：")
for year_left, cnt in hlj_yearly_counts.items():
    print(f"  {year_left}年：{cnt}个")

### 步骤2：验证作物栅格（2010-2019年）并统一CRS（保持不变）
print("\n=== 步骤2：验证2010-2019年作物栅格路径并统一CRS ===")
# 选择2010年栅格作为CRS样本（确保多年栅格CRS一致）
sample_year = 2010
sample_raster_path = corn_raster_paths[sample_year] if os.path.exists(corn_raster_paths[sample_year]) else \
wheat_raster_paths[sample_year]
with rasterio.open(sample_raster_path) as src:
    crop_crs = src.crs.to_string()
print(f"作物栅格CRS（以{sample_year}年为例）：{crop_crs}")

# 火点坐标转换（适配栅格CRS，保留所有年份火点）
if crop_crs != "EPSG:4326":
    print(f"正在将所有年份火点坐标从WGS84转换到{crop_crs}...")
    coords = hlj_fires.apply(
        lambda x: crs_transform(x["longitude"], x["latitude"], src_crs="EPSG:4326", dst_crs=crop_crs),
        axis=1
    )
    hlj_fires["x_crop"] = [c[0] for c in coords]
    hlj_fires["y_crop"] = [c[1] for c in coords]
else:
    hlj_fires["x_crop"] = hlj_fires["longitude"]
    hlj_fires["y_crop"] = hlj_fires["latitude"]
print("所有年份火点坐标转换完成")

#### 步骤2.1：分年份验证作物栅格有效性（保持不变）
print("\n=== 步骤2.1 分年份验证玉米+小麦栅格有效性（2010-2019） ===")
for crop_type in ["玉米", "小麦"]:
    print(f"\n【{crop_type}栅格分年份验证】")
    crop_paths = corn_raster_paths if crop_type == "玉米" else wheat_raster_paths
    crop_cfg = CROP_CONFIG[crop_type]

    for year in ANALYSIS_YEARS:
        sample_path = crop_paths.get(year, None)
        if not sample_path or not os.path.exists(sample_path):
            print(f"  {year}年：栅格不存在 → {sample_path}")
            continue

        # 统计该年份栅格的有效像素
        with rasterio.open(sample_path) as src:
            crop_data = src.read(1)
            total_pixels = crop_data.size
            # 过滤无效值和超范围DOY
            valid_mask = ~np.any([np.isclose(crop_data, nd, atol=1e-30) for nd in crop_cfg["nodata"]], axis=0)
            valid_mask = valid_mask & (crop_data >= crop_cfg["valid_doy"][0]) & (crop_data <= crop_cfg["valid_doy"][1])
            total_valid = np.sum(valid_mask)
            valid_ratio = (total_valid / total_pixels) * 100 if total_pixels > 0 else 0

        print(f"  {year}年：总像素={total_pixels}，有效像素={total_valid}（占比{valid_ratio:.2f}%）")

        # 每3年可视化一次
        if year % 3 == 0:  # 2010、2013、2016、2019年可视化
            fig, ax = plt.subplots(figsize=(12, 10))
            crop_data_valid = np.where(valid_mask, crop_data, np.nan)  # 无效值设为NaN
            im = ax.imshow(
                crop_data_valid,
                extent=[src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top],
                cmap="YlOrRd", alpha=0.8,
                vmin=crop_cfg["valid_doy"][0], vmax=crop_cfg["valid_doy"][1]
            )
            # 叠加黑龙江边界
            hlj_county_crs = hlj_county.to_crs(src.crs)
            hlj_county_crs.boundary.plot(ax=ax, color="black", linewidth=0.5)

            plt.colorbar(im, label=f"{crop_type}{year}年成熟DOY（有效范围）")
            plt.title(f"黑龙江省{crop_type}{year}年有效成熟DOY栅格")
            plt.xlabel("经度")
            plt.ylabel("纬度")
            save_path = os.path.join(OUTPUT_DIR, str(year), f"{crop_type}{year}年有效栅格可视化.png")
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"  {year}年栅格可视化已保存 → {save_path}")

#### 步骤2.2：分年份主产区抽样验证（保持不变）
print("\n=== 步骤2.2 分年份主产区抽样验证（2010-2019） ===")
# 双作物主产区抽样点（覆盖2010、2015、2019三个关键年份）
sample_years = [2010, 2015, 2019]  # 选取代表性年份
sample_points = {
    "玉米": [("绥化", 127.0, 46.6), ("齐齐哈尔", 123.9, 47.3)],  # 玉米主产区
    "小麦": [("黑河", 127.5, 50.2), ("佳木斯", 130.3, 46.8)]  # 小麦主产区
}

for year in sample_years:
    print(f"\n【{year}年抽样验证】")
    for crop_type, points in sample_points.items():
        crop_paths = corn_raster_paths if crop_type == "玉米" else wheat_raster_paths
        for name, lon, lat in points:
            # 坐标转换
            sample_x_crop, sample_y_crop = crs_transform(lon, lat, src_crs="EPSG:4326", dst_crs=crop_crs)
            # 提取DOY（开启debug）
            sample_doy = get_crop_maturity(
                fire_x=sample_x_crop,
                fire_y=sample_y_crop,
                crop_type=crop_type,
                year=year,  # 使用当前抽样年份
                crop_raster_paths=crop_paths,
                debug=True
            )
            # 输出结果
            print(f"  {crop_type}@{name}：")
            print(f"    坐标：经度{lon:.2f}，纬度{lat:.2f}（转换后x={sample_x_crop:.2f}, y={sample_y_crop:.2f}）")
            print(f"    有效成熟DOY：{sample_doy}")

### 步骤3：提取双作物有效DOY并匹配窗口期（保持不变）
print("\n=== 步骤3：提取2010-2019年作物有效DOY与窗口期匹配 ===")
# 3.1 处理玉米栅格（按火点年份关联对应栅格）
print("正在处理玉米栅格（2010-2019年，过滤无效值65536等）...")
hlj_fires["玉米成熟DOY"] = hlj_fires.apply(
    lambda row: get_crop_maturity(
        fire_x=row["x_crop"],
        fire_y=row["y_crop"],
        crop_type="玉米",
        year=row["year_left"],  # 用当前火点的"year"字段匹配栅格年份
        crop_raster_paths=corn_raster_paths,
        debug=False
    ),
    axis=1
)
hlj_fires["位于玉米区"] = hlj_fires.apply(lambda row: pd.notna(row["玉米成熟DOY"]), axis=1)
hlj_fires["玉米窗口期内"] = hlj_fires.apply(
    lambda row: is_in_window(row["doy"], row["玉米成熟DOY"], WINDOW_DAYS),
    axis=1
)

# 3.2 处理小麦栅格（按火点年份关联对应栅格）
print("正在处理小麦栅格（2010-2019年，过滤NoData）...")
hlj_fires["小麦成熟DOY"] = hlj_fires.apply(
    lambda row: get_crop_maturity(
        fire_x=row["x_crop"],
        fire_y=row["y_crop"],
        crop_type="小麦",
        year=row["year_left"],  # 用当前火点的"year"字段匹配栅格年份
        crop_raster_paths=wheat_raster_paths,
        debug=False
    ),
    axis=1
)
hlj_fires["位于小麦区"] = hlj_fires.apply(lambda row: pd.notna(row["小麦成熟DOY"]), axis=1)
hlj_fires["小麦窗口期内"] = hlj_fires.apply(
    lambda row: is_in_window(row["doy"], row["小麦成熟DOY"], WINDOW_DAYS),
    axis=1
)

# 按年份统计作物匹配结果
print("\n各年份作物匹配统计结果（已过滤无效值）：")
yearly_crop_stats = []
for year in ANALYSIS_YEARS:
    yearly_fires = hlj_fires[hlj_fires["year_left"] == year]
    if len(yearly_fires) == 0:
        continue
    corn_cnt = yearly_fires["位于玉米区"].sum()
    corn_window_cnt = yearly_fires[yearly_fires["位于玉米区"]]["玉米窗口期内"].sum()
    wheat_cnt = yearly_fires["位于小麦区"].sum()
    wheat_window_cnt = yearly_fires[yearly_fires["位于小麦区"]]["小麦窗口期内"].sum()
    yearly_crop_stats.append({
        "年份": year,
        "总火点": len(yearly_fires),
        "位于玉米区": corn_cnt,
        "玉米窗口期内": corn_window_cnt,
        "位于小麦区": wheat_cnt,
        "小麦窗口期内": wheat_window_cnt
    })
# 转换为DataFrame并打印
yearly_crop_df = pd.DataFrame(yearly_crop_stats)
print(yearly_crop_df.to_string(index=False))
# 保存统计结果
yearly_crop_df.to_csv(
    os.path.join(OUTPUT_DIR, "各年份作物匹配统计.csv"),
    index=False, encoding="utf-8-sig"
)

### 步骤4：火灾分类与分年定量估算（保持不变）
print("\n=== 步骤4：2010-2019年火灾分类与分年定量估算 ===")
# 计算火灾类型（全量数据）
hlj_fires["火灾类型"] = hlj_fires.apply(classify_fire, axis=1)

# 1. 总统计（2010-2019年）
fire_count = hlj_fires["火灾类型"].value_counts()
fire_frp = hlj_fires.groupby("火灾类型")["frp"].sum()
total_count = len(hlj_fires)
total_frp = hlj_fires["frp"].sum()
agri_types = ["玉米秸秆焚烧", "小麦秸秆焚烧", "混合作物焚烧"]
agri_count = sum(fire_count.get(t, 0) for t in agri_types)
agri_frp = sum(fire_frp.get(t, 0) for t in agri_types)
agri_count_ratio = (agri_count / total_count) * 100 if total_count > 0 else 0
agri_frp_ratio = (agri_frp / total_frp) * 100 if total_frp > 0 else 0

print(f"\n=== 黑龙江省火灾总分类结果（2010-2019年） ===")
print(f"1. 总火点数量：{total_count} 个 | 总FRP：{total_frp:.2f} MW")
print("\n各类型火灾详情：")
for fire_type in agri_types + ["非农业火灾"]:
    cnt = fire_count.get(fire_type, 0)
    frp_val = fire_frp.get(fire_type, 0)
    print(
        f"- {fire_type}：{cnt} 个（{cnt / total_count * 100:.2f}%）| FRP {frp_val:.2f} MW（{frp_val / total_frp * 100:.2f}%）"
    )
print(f"\n农业焚烧总占比：")
print(f"- 数量占比：{agri_count_ratio:.2f}% | FRP占比：{agri_frp_ratio:.2f}%")

# 2. 分年份统计
print("\n=== 各年份火灾分类结果 ===")
yearly_fire_stats = []
for year in ANALYSIS_YEARS:
    yearly_fires = hlj_fires[hlj_fires["year_left"] == year]
    if len(yearly_fires) == 0:
        continue
    # 各类型数量
    cnt = yearly_fires["火灾类型"].value_counts()
    # 各类型FRP
    frp = yearly_fires.groupby("火灾类型")["frp"].sum()
    # 农业焚烧合计
    yearly_agri_count = sum(cnt.get(t, 0) for t in agri_types)
    yearly_agri_frp = sum(frp.get(t, 0) for t in agri_types)
    # 保存统计
    yearly_fire_stats.append({
        "年份": year,
        "总火点": len(yearly_fires),
        "玉米秸秆焚烧（个）": cnt.get("玉米秸秆焚烧", 0),
        "小麦秸秆焚烧（个）": cnt.get("小麦秸秆焚烧", 0),
        "混合作物焚烧（个）": cnt.get("混合作物焚烧", 0),
        "非农业火灾（个）": cnt.get("非农业火灾", 0),
        "农业焚烧占比（%）": (yearly_agri_count / len(yearly_fires)) * 100 if len(yearly_fires) > 0 else 0,
        "农业焚烧FRP（MW）": yearly_agri_frp
    })
# 转换为DataFrame并打印
yearly_fire_df = pd.DataFrame(yearly_fire_stats)
print(yearly_fire_df.to_string(index=False))
# 保存分年统计结果
yearly_fire_df.to_csv(
    os.path.join(OUTPUT_DIR, "各年份火灾分类统计.csv"),
    index=False, encoding="utf-8-sig"
)

### 步骤5：FY秸秆燃烧数据验证（保持不变）
print("\n=== 步骤5：FY秸秆燃烧数据验证（2010-2019年） ===")
fy_hlj_validated = None

if FY_CSV and os.path.exists(FY_CSV):
    try:
        fy_df = pd.read_excel(FY_CSV, engine="openpyxl")
    except Exception as e:
        print(f"读取FY Excel错误 → {str(e)}，跳过验证")
    else:
        # 列名清理与重命名
        fy_df.columns = fy_df.columns.str.strip().str.replace(r'[^\w\u4e00-\u9fa5]', '', regex=True)
        column_mapping = {"中心经度": "longitude", "中心纬度": "latitude", "时间": "acq_date"}
        fy_df = fy_df.rename(columns=column_mapping)

        # 必要字段检查
        required_cols = ["longitude", "latitude", "acq_date"]
        if not all(col in fy_df.columns for col in required_cols):
            print(f"FY数据缺少必要列（需{required_cols}），跳过验证")
        else:
            # 数据清洗（提取年份）
            fy_df = fy_df[required_cols].dropna()
            fy_df["acq_date"] = pd.to_datetime(fy_df["acq_date"], errors="coerce").dropna()
            fy_df["year"] = fy_df["acq_date"].dt.year  # FY数据年份字段
            fy_df["doy"] = fy_df["acq_date"].dt.dayofyear
            fy_df = fy_df[fy_df["year"].isin(ANALYSIS_YEARS)]  # 筛选2010-2019年

            if len(fy_df) == 0:
                print("FY数据中无2010-2019年有效记录，跳过验证")
            else:
                # 空间筛选黑龙江省
                fy_gdf = gpd.GeoDataFrame(
                    fy_df, geometry=gpd.points_from_xy(fy_df["longitude"], fy_df["latitude"]), crs="EPSG:4326"
                )
                fy_hlj = gpd.sjoin(fy_gdf, hlj_county, how="inner", predicate="within").drop_duplicates()

                if len(fy_hlj) == 0:
                    print("FY数据中无黑龙江省内火点，跳过验证")
                else:
                    # 坐标转换
                    fy_hlj["x_crop"] = fy_hlj["longitude"] if crop_crs == "EPSG:4326" else [
                        crs_transform(x, y)[0] for x, y in zip(fy_hlj["longitude"], fy_hlj["latitude"])
                    ]
                    fy_hlj["y_crop"] = fy_hlj["latitude"] if crop_crs == "EPSG:4326" else [
                        crs_transform(x, y)[1] for x, y in zip(fy_hlj["longitude"], fy_hlj["latitude"])
                    ]

                    # 提取双作物有效DOY（按FY数据年份匹配栅格）
                    fy_hlj["玉米成熟DOY"] = fy_hlj.apply(
                        lambda row: get_crop_maturity(
                            row["x_crop"], row["y_crop"], "玉米", row["year_left"], corn_raster_paths
                        ), axis=1
                    )
                    fy_hlj["小麦成熟DOY"] = fy_hlj.apply(
                        lambda row: get_crop_maturity(
                            row["x_crop"], row["y_crop"], "小麦", row["year_left"], wheat_raster_paths
                        ), axis=1
                    )

                    # 计算分类条件
                    fy_hlj["位于玉米区"] = fy_hlj.apply(lambda row: pd.notna(row["玉米成熟DOY"]), axis=1)
                    fy_hlj["位于小麦区"] = fy_hlj.apply(lambda row: pd.notna(row["小麦成熟DOY"]), axis=1)
                    fy_hlj["玉米窗口期内"] = fy_hlj.apply(
                        lambda row: is_in_window(row["doy"], row["玉米成熟DOY"], WINDOW_DAYS), axis=1
                    )
                    fy_hlj["小麦窗口期内"] = fy_hlj.apply(
                        lambda row: is_in_window(row["doy"], row["小麦成熟DOY"], WINDOW_DAYS), axis=1
                    )
                    fy_hlj["火灾类型"] = fy_hlj.apply(classify_fire, axis=1)
                    fy_hlj_validated = fy_hlj.copy()

                    # 输出FY分年验证结果
                    print("\nFY数据分年验证结果：")
                    fy_yearly_stats = []
                    for year in ANALYSIS_YEARS:
                        fy_yearly = fy_hlj[fy_hlj["year_left"] == year]
                        if len(fy_yearly) == 0:
                            continue
                        agri_cnt = fy_yearly[fy_yearly["火灾类型"].isin(agri_types)].shape[0]
                        fy_yearly_stats.append({
                            "年份": year,
                            "FY火点总数": len(fy_yearly),
                            "农业焚烧火点": agri_cnt,
                            "农业焚烧占比（%）": (agri_cnt / len(fy_yearly)) * 100 if len(fy_yearly) > 0 else 0
                        })
                    fy_yearly_df = pd.DataFrame(fy_yearly_stats)
                    print(fy_yearly_df.to_string(index=False))
                    # 保存FY分年结果
                    fy_yearly_df.to_csv(
                        os.path.join(OUTPUT_DIR, "FY数据分年验证统计.csv"),
                        index=False, encoding="utf-8-sig"
                    )
