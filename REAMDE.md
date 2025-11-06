# Core Tasks 1 & 3: Spatiotemporal Patterns & Long-Term Trends of Fire Activity

This section focuses on Core Task 1 (Spatio-Temporal Patterns of Fire Activity) and Core Task 3 (Long-Term Spatio-Temporal Trends, 2010–2019) of the project.Both tasks target Heilongjiang Province (China’s major grain-producing region) and leverage remote sensing, geospatial, and phenological data to address.

## Data Preparation
### Preprocessing Workflow
To ensure consistency and accuracy across analyses, the following preprocessing steps were implemented (refer to Task1.py & Task3.py):
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
<img width="541" height="234" alt="image" src="https://github.com/user-attachments/assets/230aeaec-7e86-4a02-a4a5-5dd43104a2c9" />
- October is the absolute peak for fires, while months like January, June, July, and December have very few events. This aligns with post-harvest seasons (autumn for corn/wheat) when farmers often burn residues to clear fields.
- Spring (March–May) and Autumn (September–November) dominate, accounting for 46.0% and 45.7% of total fires respectively. Summer (4.3%) and Winter (4.0%) have minimal fire activity—because summer is growing season and winter is too cold for widespread burning.


