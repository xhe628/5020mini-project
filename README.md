# 5020 Mini-Project

# Core Tasks 1 & 3: Spatiotemporal Patterns & Long-Term Trends of Fire Activity

This section focuses on Core Task 1 (Spatio-Temporal Patterns of Fire Activity) and Core Task 3 (Long-Term Spatio-Temporal Trends, 2010–2019) of the project.Both tasks target Heilongjiang Province (China’s major grain-producing region) and leverage remote sensing, geospatial, and phenological data to address.

## Data Preparation
### Preprocessing Workflow
To ensure consistency and accuracy across analyses, the following preprocessing steps were implemented (refer to [Task1.py](https://github.com/xhe628/5020mini-project/blob/main/Task1.py) & [Task3.py](https://github.com/xhe628/5020mini-project/blob/main/Task3.py)):
#### Coordinate System Unification: 
Convert all geospatial data (e.g., county boundaries, fire points) to EPSG:4326 (WGS84)—a universal geographic coordinate system that enables cross-dataset spatial matching.
#### Time Dimension Extraction: 
Derive year, month, week (ISO week), and season from MODIS fire acquisition dates (acq_date). Seasonal division follows meteorological classification method:
Bins: [0,2,5,8,11,12] → Labels: Winter (Dec-Feb), Spring (Mar-May), Summer (Jun-Aug), Autumn (Sep-Nov)
#### Study Area Filtering: 
Restrict fire points to Heilongjiang Province using dual validation: Spatial bounds: Longitude (121°E–135°E) & Latitude (43°N–53°N); Administrative join: Spatial overlap with Heilongjiang’s county boundaries (CHN_County.shp) to exclude non-provincial fire points.

## Reasearch Method
### Core Task 1: Spatiotemporal Patterns of Fire Activity
The methodology is divided into temporal pattern analysis (to address seasonality/hotspot weeks) and spatial pattern analysis (to address geographic distribution).
#### Temporal Pattern Analysis
#### (1) Monthly & Seasonal Distribution
- Step 1: Aggregate fire counts by month and season for Heilongjiang Province (filtered via preprocessing).
- Step 2: Visualize results with: Monthly distribution: Bar chart (x=month, y=fire count) to identify peak months (e.g., post-harvest September–October). Seasonal distribution: Pie chart (with percentage labels) to quantify fire share across seasons (e.g., Autumn as the dominant burning season).

#### (2)Hotspot Weeks Identification
To go beyond "simple monthly counts" (Doc 1 §1-35), we use a data-driven threshold to define hotspot weeks:
- Step 1: Calculate average weekly fire counts (10-year average: 2010–2019) by grouping data by year and week.
- Step 2: Set the hotspot threshold as the 90th percentile of average weekly counts (avoids subjective peak definition).
- Step 3: Flag weeks with average counts ≥ threshold as "hotspot weeks" and visualize with a line plot (x=week number, y=average count) + red scatter points for hotspots.

#### Spatial Pattern Analysis
#### (1) Geographic Distribution of Fire Types
- Step 1: Classify fires into 4 types (using crop phenological data):
Maize straw burning, Wheat straw burning, Mixed crop burning, Non-agricultural fires.
- Step 2: Overlay fire points on Heilongjiang’s county boundaries (light gray base map) using a scatter plot. Use high-contrast colors for fire types to enable clear spatial differentiation: Maize: #ff6b6b (red), Wheat: #9b59b6 (purple), Non-agricultural: #4ecdc4 (teal), Mixed: #ffa500 (orange).

#### (2) County-Level Fire Density
- Step 1: Perform a spatial join between Heilongjiang’s counties and fire points to count fires per county.
- Step 2: Visualize density with a choropleth map (colormap: YlOrRd), where darker red indicates higher fire counts (highlights "hotspot counties").

### Core Task 3: Long-Term Trends (2010–2019)
The methodology focuses on county-level trend quantification and provincial-level trend overview to identify reductions or shifts in straw burning.

#### County-Level Trend Calculation
- Step 1: Filter data to 2010–2019 and split by fire type (maize straw, wheat straw, non-agricultural fires).
- Step 2: Compute annual fire counts per county (group by 县级 and year).
- Step 3: Quantify trends using linear regression: For each county’s annual count series, calculate the trend slope (via scipy.stats.linregress). The slope reflects the direction (positive=increase, negative=decrease) and magnitude of change.
- Step 4: Classify trends into 3 categories (objective slope thresholds to ensure consistency):

| Trend Category       | Slope Range        | Interpretation                                         |
|----------------------|--------------------|--------------------------------------------------------|
| Significant Decrease | < -0.5             | Annual fire counts decline noticeably over 10 years    |
| Basically Stable     | -0.5 ≤ slope ≤ 0.5 | Annual fire counts show no clear upward/downward trend |
| Significant Increase | > 0.5              | Annual fire counts rise noticeably over 10 years       |

### Provincial-Level Trend Overview
- Step 1: Aggregate annual fire counts by fire type (province-wide) for 2010–2019.
- Step 2: Visualize trends with line plots (x=year, y=fire count) + linear fit lines (dashed) to highlight overall direction.
- Step 3: Identify turning points by inspecting deviations from the linear fit.

  
## Result of Analysis
### Monthly Distribution & Seasonal Distribution
![Heilongjiang fire_seasonal_distribution](https://github.com/xhe628/5020mini-project/blob/main/figures/fire_seasonal_distribution.png)

- October is the absolute peak for fires, while months like January, June, July, and December have very few events. This aligns with post-harvest seasons (autumn for corn/wheat) when farmers often burn residues to clear fields.
- Spring (March–May) and Autumn (September–November) dominate, accounting for 46.0% and 45.7% of total fires respectively. The burning of straw in Spring is mainly due to the fact that farmers need to clear the remaining straw and weeds in the fields before sowing to ensure a smooth planting process and to reduce the impact of pests and diseases on the new crop season. Summer (4.3%) and Winter (4.0%) have minimal fire activity since summer is growing season and winter is too cold for widespread burning.

### Geographic Distribution of Fires
![Heilongjiang fire geografhic distribution](https://github.com/xhe628/5020mini-project/blob/main/figures/fire_geographic_distribution.png)
![Heilongjiang fire density](https://github.com/xhe628/5020mini-project/blob/main/figures/county_fire_density_heatmap.png)

- By fire type: Corn straw burning is highly concentrated in northern Heilongjiang, which makes sense since this region is a major corn-producing area. In contrast, non-agricultural fires are much more widespread across the province—no single region dominates.  
- Hotspot counties: The density heatmap highlights that dark red counties are fire "hotspots" with the highest fire counts. These counties should be prioritized for targeted prevention measures, like increased monitoring during harvest seasons. 

### Weekly Distribution and Hotspot Weeks 
![Helilongjiang fire hotsopt weeks ](https://github.com/xhe628/5020mini-project/blob/main/figures/fire_weekly_distribution.png)

-  there are two distinct clusters of "hotspot weeks" each year—specifically Week 14(around the time of Spring farming season) and Week 43(coincides precisely with the post-harvest dates). These weeks are critical for fire control, as they see over 2,033 fires on average, far above other weeks. 

### County-level Interannual Trend of Fires (2010–2019) 
![Heilongjiang County-level_Fire_Trend](https://github.com/xhe628/5020mini-project/blob/main/figures/Heilongjiang_County-level_Fire_Trend_Map.png)

At the county level:  
- Corn straw burning: Most counties show a "significant decrease" (marked in green). This suggests that policies targeting corn residue burning—like bans or alternative disposal support—have been effective in reducing such fires.  
- Wheat straw burning: Trends are mixed. Some counties show a decrease, others stay "basically stable" (orange), and a small number even increase (red). This inconsistency may reflect varying enforcement of straw burning rules across different wheat-growing areas.  
- Non-agricultural fires: The opposite trend—most counties show a "significant increase" (red). We’ll need further investigation to understand why, but possible factors include more industrial activity or accidental human-caused fires.

### Overall Trend and Linear Fitting (2010–2019) 
![Heilongjiang multi typle fire overall trend](https://github.com/xhe628/5020mini-project/blob/main/figures/Heilongjiang_County-level_Fire_Trend_Map.png)

For overall long-term trends,we find:
1. Corn straw burning:
  - Turning point: After reaching a peak in 2011, the number of fires has continued to decline, with a linear slope of -321.32, and the downward trend is significant.
  - Reason analysis:
    - Policy-driven: Starting from 2011, Heilongjiang Province gradually strengthened the policy of prohibiting straw burning, and also introduced subsidies for straw utilization (such as per-plot subsidies for straw returning to the soil, and support for biomass power generation projects), forcing farmers to reduce burning behavior.
    - Technological substitution: Promoting technologies such as straw returning to the soil, straw feed conversion, and biomass fuel, transforming straw from "burned waste" into "usable resources", reducing the demand for burning.
    - Regulatory strengthening: The environmental protection department has intensified inspections and penalties, using satellite remote sensing monitoring to precisely locate burning points, and handling violations "as soon as they are discovered", creating an effective deterrent.
2.  Wheat straw burning:
  - Turning point: The trend fluctuated significantly (such as the trough in 2013 and the recovery in 2016), the linear slope was -7.68, there was a slight overall decline but the stability was insufficient.
  - Reason analysis:
    - Policy implementation differences: The scale of wheat cultivation is smaller than that of corn. The implementation intensity and resource investment of local policies on prohibiting straw burning in wheat areas are weaker than those for corn, resulting in unstable control effects.
    - Limited utilization mode: The industrialized utilization of wheat straw (such as as feed, weaving) has not yet formed a large-scale and stable industrial chain. Farmers' alternative solutions for handling straw are insufficient, and the burning behavior is prone to fluctuate with planting income and market demand.
    - Climate and agricultural impact: If the wheat harvest period encounters rainy weather, the straw becomes humid and difficult to burn, temporarily reducing the number of fires (such as the trough in 2013 or related to this).
3. Non-agricultural Fires:
  - Turning point:After 2017, the growth accelerated, with a linear slope of 1129.25, and the upward trend was obvious.
  - Reason analysis:
    - Economic activity expansion: The industrialization and urbanization process in Heilongjiang Province has accelerated, leading to an increase in industrial production, construction activities, and urban infrastructure projects. This has resulted in more non-agricultural fire scenarios (such as open flames at construction sites and industrial waste incineration).
    - Weak regulatory system: Non-agricultural fires involve multiple industries and are scattered in various scenarios (such as industry, commerce, and domestic use of fire), making the supervision much more difficult than agricultural straw burning. The existing control measures (such as fire inspections) are unable to cover all areas, causing the number of fires to increase in tandem with economic activities.
    - Human factors combined: Urbanization leads to population concentration, and the management of life-related open flames (such as outdoor barbecues and sacrificial fires) becomes more challenging, further increasing the incidence of non-agricultural fires.
   
## Rationale for Analytical Choices
### Choices for Task 1 (Spatio-Temporal Patterns)
Dual study area filtering (bounds + admin join): Bounds alone may include non-Heilongjiang areas (e.g., adjacent Inner Mongolia); administrative join ensures 100% provincial accuracy.

High-contrast colors for fire types: Colors like red (maize) and teal (non-agricultural) have strong visual differentiation—critical for identifying spatial clusters (e.g., maize burning concentrated in western Heilongjiang).

## Choices for Task 3 (Long-Term Trends)
Linear regression for trend slope: Linear regression quantifies direction and magnitude of change (unlike moving averages, which smooth trends). A slope of -1.2, for example, means 1.2 fewer fires per year—actionable for policy evaluation.

Slope thresholds (-0.5 / 0.5): Thresholds are calibrated to 10-year data. A slope of ±0.5 translates to ±5 fires over 10 years—large enough to be a "significant" shift (not noise).






# Core Task 4 & Challenge 1: Comprehensive Comparison and FRP Analysis of Agricultural vs Non-agricultural Fires  

This section focuses on **Core Task 4 (Comprehensive Analysis of Agricultural vs Non-agricultural Fires)** and **Challenge 1 (Fire Radiative Power Analysis)**.  
Both tasks extend the prior spatiotemporal analysis to compare **fire characteristics**, including **intensity**, **seasonality**, and **diurnal distribution**, aiming to uncover the distinct behavioral and environmental patterns between agricultural and non-agricultural fire events in Heilongjiang Province.

---

## Data Preparation  

### Preprocessing Workflow  

The dataset integrates multi-year MODIS active fire data (2010–2019) with spatial and temporal metadata.  
To ensure analytical consistency, the following preprocessing pipeline was applied (refer to [`Task4&challenge1.py`](https://github.com/xhe628/5020mini-project/blob/main/task4%26challenge1.ipynb)):  

---

## Research Method  

### Core Task 4: Comprehensive Comparison of Agricultural vs Non-agricultural Fires  

The analysis focuses on three major dimensions: **fire intensity**, **monthly pattern**, and **hourly distribution**.  

#### (1) Fire Intensity Analysis  
- **Indicator:** Fire Radiative Power (FRP) was selected as the quantitative measure of fire energy output and intensity.  
- **Method:**  
  - Calculate summary statistics (mean, median, standard deviation, and 90th percentile) for FRP by fire type.  
  - Conduct a **t-test** and **Cohen’s d** effect size analysis to determine statistical significance between agricultural and non-agricultural FRP distributions.  
  - Visualize with kernel density estimation (KDE) and boxplots.  
- **Interpretation Basis:**  
  FRP directly corresponds to combustion energy; thus, higher FRP indicates larger, more destructive fires.  

#### (2) Monthly Pattern Analysis  
- **Purpose:** Identify seasonal cycles of agricultural burning vs non-agricultural fire occurrence.  
- **Method:**  
  - Aggregate fire counts by month (2010–2019).  
  - Normalize to percentages to eliminate interannual bias.  
  - Visualize via side-by-side bar charts for agricultural vs non-agricultural fires.  
- **Key Observation Metric:** Peak months correspond to harvest or dry seasons when fire occurrence probability is highest.
  
#### (3) Hourly Distribution Analysis  
- **Purpose:** Investigate diurnal burning behavior and potential human influence.  
- **Method:**  
  - Extract the hour from MODIS acquisition times.  
  - Compute and plot normalized hourly frequency for both fire categories.  
  - Interpret concentration windows (e.g., nighttime vs daytime).  

### Challenge 1: Fire Radiative Power (FRP) Comparative Analysis  

To extend the Task 4 findings, Challenge 1 quantitatively explores **FRP variations across agricultural and non-agricultural fires**, aiming to understand their environmental impact and energy characteristics.  

#### Steps:  
1. Filter the dataset by fire type.  
2. Compute descriptive FRP statistics (mean, median, max, standard deviation).  
3. Compare FRP distributions visually and statistically (KDE + t-test).  
4. Interpret implications for fire management and resource allocation.  

---

## Result of Analysis  

### 🔥Fire Intensity  
- **Agricultural Fires:**  
  - Median FRP ≈ **8–9**, indicating **low-intensity, small-scale burns**.  
  - Occasional maize-burning events exhibit higher FRP spikes, but overall remain mild.  
- **Non-agricultural Fires:**  
  - Median FRP ≈ **10.8**, reaching up to **1824**, revealing **high-intensity, large-scale events**.  
  - Statistically significant difference between categories (**p < 0.01**, strong effect size).  
- **Implication:**  
  Agricultural fires, while numerous, contribute less to total radiative energy release.  
  Non-agricultural fires, though fewer, release disproportionately high energy, implying greater environmental and economic risk.

### 📆 Monthly Pattern  
- **Agricultural fires:** Concentrated between **July and October**, aligning perfectly with **harvest seasons** and **straw-burning periods**.  
- **Non-agricultural fires:** Exhibit a **bimodal distribution** — peaks in **spring (March–April)** and **autumn (October)** — reflecting **multiple ignition sources**, including industrial, accidental, and land-clearing fires.  
- **Implication:**  
  Agricultural fires are **strongly seasonal and policy-sensitive**, while non-agricultural fires reflect **broader socioeconomic and climatic variability**.  

### ⏰ Hourly Distribution  
- **Agricultural fires:**  
  - Concentrated during **nighttime (2–5 a.m.)**, peaking around **4 a.m.**  
  - Suggests **intentional nighttime burning** behavior to avoid regulation and detection.  
- **Non-agricultural fires:**  
  - Distributed **uniformly throughout the day**, indicating **diverse and less-controlled ignition sources**.  
- **Implication:**  
  Temporal fire control policies should prioritize nighttime satellite monitoring and targeted public awareness in rural regions.  

📊 **Figure. Fire Comparison**  
![Figure 7: fire comprehensive_analysis](https://github.com/xhe628/5020mini-project/blob/main/figures/Fire%20characteristic%20compariaon.jpg)

---

## Challenge 1 Results Summary  

 p=0.0000, Cohen's d=-0.063
| Category | Average FRP | Median FRP | High Intensity Ratio |
|-----------|------------|-------------|-----------|
| Wheat | 14.28 | 8.80 | 3.5% |
| Maize | 17.61 | 8.00 | 3.9% |
| Non-agricultural Fires | 18.42 | 10.80 | 6.1% |


📊 **Figure. Summary Comparison of Fire Characteristics**  
![Figure: Comparison of Fire FRP](https://github.com/xhe628/5020mini-project/blob/main/figures/Comparison%20of%20Fire%20FRP.png)
![Figure: Comparison of Fire FRP](https://github.com/xhe628/5020mini-project/blob/main/figures/FRP%20comparison.jpg)

 **Overall Interpretation:**  
- **Agricultural fires** are **frequent but low-intensity**, tightly linked to **harvest cycles** and **localized human practices**.  
- **Non-agricultural fires** are **sporadic but highly destructive**, reflecting **industrial activity**, **urban expansion**, and **climatic vulnerability**.  

These insights support the need for **dual-strategy fire management**:  
1. **Preventive education and policy enforcement** in rural agricultural zones.  
2. **Enhanced detection and emergency response** for high-intensity non-agricultural fires.   














