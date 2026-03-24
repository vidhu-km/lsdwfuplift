import geopandas as gpd
import folium

# Load shapefile
gdf = gpd.read_file("ooipsectiongrid.shp")

# Reproject if needed
if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
    gdf = gdf.to_crs(epsg=4326)

# Add ID
gdf = gdf.reset_index().rename(columns={"index": "id"})

# Map center
centroid = gdf.geometry.centroid
center = [centroid.y.mean(), centroid.x.mean()]

m = folium.Map(location=center, zoom_start=10)

# Columns WITHOUT geometry
fields = [col for col in gdf.columns if col != "geometry"]

# Add GeoJSON layer
folium.GeoJson(
    gdf,
    tooltip=folium.GeoJsonTooltip(fields=fields),  # ✅ FIX HERE
    style_function=lambda feature: {
        "color": "blue",
        "weight": 1,
        "fillOpacity": 0.3,
    },
).add_to(m)

# Save map
m.save("map.html")

print("Open map.html in your browser")