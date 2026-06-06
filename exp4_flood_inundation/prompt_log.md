# Prompt Log - Experiment 4

Documentation of AI interactions

---

## Part 0: Initial

**prompt 1**

> read this document know the basic information, and generate empty file which are ought to be submitted

**answer 1**

> I read [Experiment4_Flood_Inundation.docx](Experiment4_Flood_Inundation.docx). It is a 2-hour lab handout for **Specialized Experiment 4: Flood Inundation Analysis (DEM-based)** in the **Smart Water Lab Series**.
>
> Main points:
>
> - **Goal:** analyze flood inundation using DEM data, spatial comparison, visualization, and flooded area percentage calculation.
> - **Learning objectives:** process DEM data, implement flood logic, create flood extent maps, calculate flooded area percentages, and validate that flooded area increases with water level.
> - **Core tasks:**
>   1. Prepare DEM data
>   2. Simulate flooding at a given water level
>   3. Visualize flood extent and inundation depth
>   4. Run dynamic water-level simulation
>   5. Validate physical correctness
> - **Deliverables:** `flood_inundation.py`, `dem_data.npy`, `flood_extent_40m.png`, `flood_extent_50m.png`, `flood_curve.png`, and `prompt_log.md`.
> - **Sample code structure:** includes `load_dem()`, `calculate_flood()`, `visualize_flood()`, and `simulate_rising_water()`.
> - **Grading:** DEM data 15%, flood calculation 25%, visualization 25%, dynamic simulation 20%, physical validation 10%, prompt log 5%.
>
> I also created empty placeholder files for the required submission items in the project folder.

## Part 1: DEM Data Preparation

**prompt 1**

> Option 1: Generate Synthetic DEM  
> Create a 100×100 grid with elevation values between 30-80m:
> - Use numpy.random for random terrain
> - Or create a simple slope pattern
>
> Option 2: Load Real DEM Data  
> Download sample DEM from:
> - USGS Earth Explorer
> - OpenTopography

**answer 1**

> The experiment allows two valid approaches for DEM preparation:
> - **Synthetic DEM**: generate a 100×100 grid with elevations in the 30-80m range using `numpy.random` or a slope pattern. This is the easiest option for testing and validation.
> - **Real DEM**: download sample elevation data from sources such as **USGS Earth Explorer** or **OpenTopography**.
>
> For a predictable first implementation, synthetic DEM data is the simplest choice.

## Part 2: Flood Simulation

**prompt 1**

> Sample Prompt:
>
> I have a 2D numpy array 'dem' representing terrain elevation (100×100). Please write Python code to:
> 1. Simulate flooding at a given water level
> 2. Create a boolean mask for flooded cells (elevation < water_level)
> 3. Calculate inundation depth for flooded cells
> 4. Calculate flooded area percentage
> 5. Return the mask, depth array, and percentage

**answer 1**

> The flood simulation logic should:
> - compare each DEM cell with the given water level
> - mark flooded cells with a boolean mask
> - compute inundation depth as `water_level - elevation` for flooded cells
> - set depth to `0` for non-flooded cells
> - calculate flooded area percentage as `(flooded cells / total cells) * 100`
>
> This returns the flooded mask, the depth array, and the flooded area percentage for later visualization and validation.

## Part 3: Visualization

**prompt 1**

> Visualization Requirements:
> 1. Original DEM as grayscale image
> 2. Flood extent as blue overlay
> 3. Inundation depth heatmap (blue color scheme)
> 4. Side-by-side comparison at different water levels
> 5. Include colorbar and title

**answer 1**

> The visualization should present the flood analysis clearly:
> - display the original DEM with a grayscale colormap
> - overlay flooded areas in blue to highlight inundation extent
> - use a blue color scheme for the depth heatmap
> - compare multiple water levels side by side for easier interpretation
> - add titles and colorbars to make the figures readable and informative

## Part 4: Dynamic Simulation

**prompt 1**

> Dynamic Simulation Tasks:
> 1. Loop through water levels from 40m to 50m
> 2. Calculate flooded percentage at each level
> 3. Create a plot: Water Level vs. Flooded Percentage
> 4. Verify: Does flooded area increase monotonically?
> 5. Document any unexpected behavior

**answer 1**

> The dynamic simulation should:
> - iterate water levels from 40m to 50m
> - compute the flooded percentage at each step
> - plot water level against flooded percentage
> - check whether flooded area increases monotonically as water level rises
> - record any unexpected behavior if the trend is not strictly increasing
>
> This section is used to validate the physical reasonableness of the flood model.

## Part 5: Validation

**prompt 1**

> Validate physical correctness.
> 1. Verify flooded area increases with water level
> 2. Check that maximum depth equals (water_level - min_elevation)
> 3. Confirm flooded percentage is between 0-100%
> 4. Validate edge cases (water below min elevation, above max elevation)

**answer 1**

> The validation step should confirm the model is physically reasonable:
> - flooded area should increase as water level rises
> - maximum depth should match `water_level - min_elevation` when the whole grid is flooded
> - flooded percentage should always stay within `0-100%`
> - edge cases should behave correctly when water is below the minimum elevation or above the maximum elevation
>
> These checks help verify that the flood simulation is consistent with the DEM data and water-level logic.

## Part 6: Optional Extensions

**prompt 1**

> add extension part
> •  Load and analyze real DEM data for a specific watershed
> •  Implement flood routing (water spreads to adjacent cells)
> •  Add building footprints as barriers to flooding
> •  Create animated GIF of rising water levels
> •  Calculate flood volume (depth × cell area × count)

**answer 1**

> The extension ideas can be supported by the experiment workflow as follows:
> - real DEM loading is already supported through the `load_dem()` function
> - flood routing can be implemented by spreading water to adjacent cells
> - building footprints can act as barriers by blocking flood propagation
> - an animated GIF can show the flood change across rising water levels
> - flood volume can be calculated from depth, cell area, and flooded cell count
>
> These extensions make the model more realistic and more useful for watershed-level analysis.

