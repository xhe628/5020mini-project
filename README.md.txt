Methodological Limitations and Uncertainties of Agricultural Burning Classification
Overview
This document provides a critical evaluation of the agricultural burning classification method, elaborates on its core uncertainties and limitations, analyzes the impact of these limitations on final estimates, and proposes improvement schemes based on multi-source data—serving as a reference for result interpretation and future research.
I. Methodological Limitations and Uncertainties
Critical Evaluation of the Classification Method
Our classification method, based on "spatial overlap with farmland" and "temporal proximity to harvest dates," offers a reasonable framework for estimating agricultural burning. However, it is subject to the following uncertainties and potential sources of error:
1. Spatial Resolution and Mixed Pixel Issues
MODIS fire pixel data has a spatial resolution of 1 km, meaning a single pixel may contain multiple land cover types (e.g., farmland, forests, residential areas).
Fires detected in such mixed pixels may be misclassified if they occur near farmland rather than within it.
The 1 km farmland map used may fail to capture small or fragmented farmland, leading to missed detections.
2. Temporal Assumptions and Fixed Harvest Windows
We assume fires occurring within 30 days after crop maturity dates are agricultural burning, but farmers may advance or delay burning due to weather, labor, or policy factors.
Crop phenological data is derived from 2010 and may not reflect changes in planting structures over the 10-year study period.
3. Data Accuracy and Representativeness Limitations
The FY straw burning validation dataset only covers a short period (August 2016–February 2017) and lacks crop type labels.
The farmland distribution map does not account for crop rotation or interannual changes in land use.
MODIS data may miss small-scale or short-duration burning events.
4. Subjectivity in Classification Rules
Thresholds for spatial proximity and temporal windows are set based on literature without rigorous sensitivity testing.
Differences in burning behaviors between crop types (e.g., corn vs. wheat) are not distinguished.
5. Confounding Fire Sources
Fires in areas adjacent to farmland (e.g., grasslands, forests) may be misclassified as agricultural burning during harvest periods.
II. Impact of Limitations on Final Estimates
These limitations may result in:
Overestimation of agricultural fires: Inclusion of non-agricultural fires in areas adjacent to farmland.
Underestimation of agricultural fires: Missed detections of small-scale or short-duration burning events.
Temporal mismatch: Discrepancies between actual burning events and simulated harvest windows.
Thus, our final estimate of agricultural burning should be interpreted as a "reasonable range" rather than a precise value.
III. Improvement Strategies: Additional Data and Methods
1. High-Resolution Land Use/Land Cover Data
Recommended datasets: Globeland30 (30m resolution) or Sentinel-2-based classification products.
Application: Replace the 1 km farmland map to more accurately distinguish farmland boundaries from other land types.
2. Nighttime Light Data (VIIRS)
Application: Exclude fires in urban and industrial areas to reduce misclassification of non-agricultural fires.
3. Meteorological Data Integration
Recommended data: Soil moisture, wind speed, temperature.
Application: Identify dry conditions favorable for wildfires to help distinguish natural fires from anthropogenic agricultural burning.
4. Road Network Data
Application: Use road proximity as a proxy for human activity to assist in identifying agricultural activity areas.
5. Local Policy and Survey Data
Recommended data: County-level straw burning ban policy implementation records, farmer survey data.
Application: Validate the relationship between classification results and policy implementation effects to improve model interpretability.
IV. Conclusion
Our classification method provides a useful preliminary framework for estimating agricultural burning, but acknowledging its limitations is critical for the reasonable interpretation of results. Future research should integrate multi-source data and further optimize classification accuracy through ground validation or high-confidence reference datasets.