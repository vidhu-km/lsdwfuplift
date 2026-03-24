import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

st.title("Polygon Selector")

# Load shapefile
gdf = gpd.read_file("ooipsectiongrid.shp")

# Ensure CRS is lat/lon for web maps
if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
    gdf = gdf.to_crs(epsg=4326)

# Add a proper ID column
gdf = gdf.reset_index().rename(columns={"index": "id"})

# Store selected indices
if "selected" not in st.session_state:
    st.session_state.selected = set()

# Compute map center safely
centroid = gdf.geometry.centroid
center = [centroid.y.mean(), centroid.x.mean()]

# Create map
m = folium.Map(location=center, zoom_start=10)

# Style function
def style_function(feature):
    idx = feature["properties"]["id"]
    if idx in st.session_state.selected:
        return {"color": "red", "weight": 3, "fillOpacity": 0.5}
    return {"color": "blue", "weight": 1, "fillOpacity": 0.2}

# Add GeoJSON layer (exclude geometry from tooltip)
geo = folium.GeoJson(
    gdf,
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(
        fields=[col for col in gdf.columns if col != "geometry"]
    ),
    name="Polygons"
)

geo.add_to(m)

# Render map
map_data = st_folium(m, height=600, width=800)

# Handle clicks
if map_data and map_data.get("last_active_drawing"):
    clicked = map_data["last_active_drawing"]

    # Get ID from properties (important!)
    clicked_idx = clicked["properties"]["id"]

    if clicked_idx in st.session_state.selected:
        st.session_state.selected.remove(clicked_idx)
    else:
        st.session_state.selected.add(clicked_idx)

# Show selected polygons
if st.session_state.selected:
    selected_df = gdf[gdf["id"].isin(st.session_state.selected)]

    st.write("Selected polygons:")
    st.dataframe(selected_df.drop(columns="geometry"))

    csv = selected_df.drop(columns="geometry").to_csv(index=False)

    st.download_button(
        "Download CSV",
        csv,
        file_name="selected_polygons.csv",
        mime="text/csv"
    )