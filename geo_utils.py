import json
import geojson
from shapely.geometry import shape
from pathlib import Path

import osmnx as ox
import geopandas as gpd
import matplotlib.pyplot as plt

def get_bounds_from_geojson(file_path):
    with open(file_path) as f:
        data = geojson.load(f)
    
    # Extract the geometry
    geometry = data['features'][0]['geometry']
    
    # Get the bounding box
    bounds = shape(geometry).bounds
    return bounds

# ___OSMNX_____
def download_buildings(bounds):
    min_lon, min_lat, max_lon, max_lat = bounds
    # Get building footprints within the bounding box with all tags
    buildings = ox.geometries_from_bbox(max_lat, min_lat, max_lon, min_lon, tags={'building': True})
    return buildings

def clean_geodataframe(gdf):
    # Convert any unsupported field types to strings
    for col in gdf.columns:
        if gdf[col].dtype == 'object':
            gdf[col] = gdf[col].apply(lambda x: str(x) if isinstance(x, list) else x)
    return gdf

def save_to_geojson(buildings, output_file):
    buildings = clean_geodataframe(buildings)
    buildings.to_file(output_file, driver='GeoJSON')

def load_and_plot_building(file_path):
    # Load the GeoJSON file
    buildings = gpd.read_file(file_path)
    
    # Select the first building (or another if preferred)
    building = buildings.iloc[0]
    
    # Print all metadata for the selected building
    print("Metadata for the selected building:")
    print(building)
    
    # Plot the selected building
    fig, ax = plt.subplots()
    buildings.plot(ax=ax, color='lightgrey', edgecolor='black')
    gpd.GeoSeries([building.geometry]).plot(ax=ax, color='red')
    plt.show()

def calculate_statistics(buildings):
    # Check the original CRS
    print(f"Original CRS: {buildings.crs}")
    
    # Project the GeoDataFrame to UTM (or another suitable coordinate system)
    buildings_projected = buildings.to_crs(epsg=32613)  # UTM zone 13N
    print(f"Projected CRS: {buildings_projected.crs}")
    
    # Number of buildings
    num_buildings = len(buildings_projected)
    
    # Total area covered by buildings
    buildings_projected['area'] = buildings_projected.geometry.area
    total_area = buildings_projected['area'].sum()
    
    # Average area per building
    avg_area = buildings_projected['area'].mean()

    print(f"Number of buildings: {num_buildings}")
    print(f"Total area covered by buildings: {total_area:.2f} square meters")
    print(f"Average area per building: {avg_area:.2f} square meters")


if __name__ == "__main__":
    fpath = Path('D:/data/snowload/KML_shape/Breckenridge/breckenridge.geojson')
    bounds = get_bounds_from_geojson(fpath)
    print(f"Bounding box coordinates: {bounds}")
    
    # Download buildings data
    buildings = download_buildings(bounds)

    # Save the buildings data to a GeoJSON file
    output_file = Path('D:/data/snowload/KML_shape/Breckenridge/buildings_osmnx.geojson')
    save_to_geojson(buildings, output_file)
    
    print(f"Buildings data saved to: {output_file}")

    # Load and plot one of the buildings
    load_and_plot_building(output_file)

    # Calculate and print statistics
    calculate_statistics(buildings)
