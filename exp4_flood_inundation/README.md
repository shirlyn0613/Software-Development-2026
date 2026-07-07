# Experiment 4 - Flood Inundation Analysis

DEM-based flood inundation analysis for Specialized Experiment 4. The project generates or loads DEM data, computes flooded cells and inundation depth, visualizes flood extent, runs a rising-water simulation, and validates physical correctness.

## Quick Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the complete experiment pipeline:

```bash
python example_usage.py
```

Or run only the main flood analysis:

```bash
python flood_inundation.py
```

Run tests:

```bash
python -m unittest discover -s tests
```

Generate the validation report:

```bash
python validation_suite.py
```

## Project Structure

```text
.
|-- flood_inundation.py          Main DEM, flood, plotting, and extension logic
|-- example_usage.py             End-to-end entry point
|-- validation_suite.py          Physical validation report generator
|-- validation_report.txt        Generated verification report
|-- requirements.txt             Python dependencies
|-- README.md                    Project documentation
|-- prompt_log.md                AI interaction record
|-- tests/
|   `-- test_flood_inundation.py Automated unit tests
|-- visualization/
|   |-- __init__.py
|   `-- animation.py             Static and animated visualization helpers
|-- dem_data.npy                 Generated synthetic DEM
|-- dem_data_extended.npy        DEM with building-barrier extension
|-- flood_extent_40m.png         Flood output at 40 m
|-- flood_extent_50m.png         Flood output at 50 m
|-- flood_curve.png              Water level vs flooded percentage
|-- flood_stages.png             Multi-stage visualization
|-- flood_rising.gif             Rising-water animation
`-- flood_volume_45m.json        Flood volume summary at 45 m
```

## Model Logic

```text
Flooded cell:     elevation < water_level
Depth:            max(water_level - elevation, 0)
Flooded percent:  flooded_cells / total_cells * 100
Volume:           sum(depth) * cell_area
```

The default DEM is a 100x100 synthetic terrain grid. If `dem_data.npy` already exists and is valid, the script reuses it; otherwise it generates a reproducible DEM.

## Outputs

- `flood_extent_40m.png` and `flood_extent_50m.png`: terrain map plus flood depth view
- `flood_curve.png`: flooded percentage across 40-50 m water levels
- `flood_stages.png`: side-by-side multi-level comparison
- `flood_rising.gif`: animated rising-water visualization
- `validation_report.txt`: physical validation report

## Validation Coverage

The validation suite checks:

- DEM dimensions and elevation range
- no flooding below minimum elevation
- full flooding above maximum elevation
- maximum depth relationship
- flooded percentage bounds
- monotonic flooded percentage for rising water levels
- monotonic flood volume and maximum depth

## Dependencies

Dependencies are listed in `requirements.txt`:

- `numpy`
- `matplotlib`
- `Pillow`
