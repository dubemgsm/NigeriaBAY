import os
import geopandas as gpd
import pandas as pd
import folium
import branca.colormap as cm

def create_map_processed():
    processed_dir = "/workspaces/NigeriaBAY/data/processed"
    clean_dir = "/workspaces/NigeriaBAY/data/clean"
    output_dir = "/workspaces/NigeriaBAY/outputs/maps"
    os.makedirs(output_dir, exist_ok=True)
    
    # Shape Data (from data/clean)
    lga_shp = os.path.join(clean_dir, "nga_shp/nga_admin2.shp")
    
    # Processed Data (from data/processed)
    conflict_csv = os.path.join(processed_dir, "conflict.csv")
    schools_csv = os.path.join(processed_dir, "schools.csv")
    idp_csv = os.path.join(processed_dir, "IDP.csv")
    summary_csv = os.path.join(processed_dir, "nga_bay_lga_summary.csv")
    
    output_map = os.path.join(output_dir, "education_risk_map.html")
    output_map_disruption = os.path.join(output_dir, "education_disruption_map.html")
    
    if not all(os.path.exists(f) for f in [lga_shp, summary_csv, conflict_csv, schools_csv, idp_csv]):
        print("Missing required spatial or tabular files for mapping.")
        return

    print("Loading datasets (Boundaries from clean, points/metrics from processed)...")
    # Load boundaries (from data/clean)
    gdf_lgas = gpd.read_file(lga_shp)
    gdf_lgas["LGA"] = gdf_lgas["adm2_name"].replace({"Tarmua": "Tarmuwa"})
    
    # Load summary metrics (from data/processed)
    df_metrics = pd.read_csv(summary_csv)
    top_10_lgas = df_metrics.nlargest(10, "risk_score")["LGA"].tolist()
    
    # Merge boundaries with summary metrics
    print("Merging boundaries with summary metrics...")
    gdf_merged = gdf_lgas.merge(df_metrics, on="LGA", how="inner")
    gdf_merged = gdf_merged.to_crs("EPSG:4326")
    
    # Calculate bounds for map restrictions (removing the rest of the country/world)
    bounds = gdf_merged.total_bounds  # [lon_min, lat_min, lon_max, lat_max]
    pad = 0.4
    min_lon = float(bounds[0] - pad)
    min_lat = float(bounds[1] - pad)
    max_lon = float(bounds[2] + pad)
    max_lat = float(bounds[3] + pad)
    
    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2
    
    # Round risk score for display
    gdf_merged["risk_score_disp"] = gdf_merged["risk_score"].round(4)
    
    # Initialize Folium Map restricted only to BAY states
    m = folium.Map(
        location=[center_lat, center_lon], 
        zoom_start=7, 
        tiles=None,
        control_scale=True,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon,
        max_bounds=True,
        min_zoom=6,
        max_zoom=12
    )
    
    # Fit map bounds to the BAY states extent
    m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])
    
    # Define color scale for Risk Score (Yellow -> Orange -> Red)
    colormap = cm.linear.YlOrRd_09.scale(0.0, 1.0)
    colormap.caption = "Normalized LGA Risk Score (0 = Low, 1 = High)"
    m.add_child(colormap)

    # Map Title removed as requested
    
    # Style function for risk score choropleth (lighter grey outline for normal LGAs)
    def style_fn(feature):
        score = feature["properties"]["risk_score"]
        return {
            "fillColor": colormap(score) if pd.notnull(score) else "#ececec",
            "color": "#777777",
            "weight": 0.8,
            "fillOpacity": 0.80
        }
        
    def highlight_fn(feature):
        return {
            "weight": 2.5,
            "color": "#000000",
            "fillOpacity": 0.90
        }

    # Add permanent static LGA boundaries wireframe (always visible)
    folium.GeoJson(
        gdf_merged,
        style_function=lambda x: {
            "fillColor": "transparent",
            "color": "#777777",
            "weight": 0.8,
            "fillOpacity": 0.0
        },
        control=False,
        interactive=False
    ).add_to(m)

    # Add GeoJson Choropleth layer
    folium.GeoJson(
        gdf_merged,
        name="LGA Vulnerability (Risk Score)",
        style_function=style_fn,
        highlight_function=highlight_fn,
        tooltip=folium.GeoJsonTooltip(
            fields=["LGA", "risk_score_disp", "idp_population", "closed_schools"],
            aliases=["LGA Name:", "Risk Score:", "IDP Population:", "Closed Schools:"],
            localize=True,
            sticky=False,
            labels=True,
            style="""
                background-color: #F0F2F6;
                border: 2px solid #5F6368;
                font-family: sans-serif;
                font-size: 13px;
                padding: 10px;
                border-radius: 4px;
            """
        )
    ).add_to(m)

    # Highlight top 10 LGAs: add a thick black border layer on top
    gdf_top10 = gdf_merged[gdf_merged["LGA"].isin(top_10_lgas)]
    folium.GeoJson(
        gdf_top10,
        name="Top 10 High-Risk LGAs Outline",
        style_function=lambda x: {
            "fillColor": "transparent",
            "color": "#000000",
            "weight": 6.5,
            "fillOpacity": 0.0
        },
        control=False,
        interactive=False
    ).add_to(m)

    # Add text labels for top 5 LGAs (showing LGA name only)
    gdf_top5 = gdf_merged.sort_values(by="risk_score", ascending=False).head(5)
    for rank, (idx, row) in enumerate(gdf_top5.iterrows(), 1):
        centroid = row.geometry.representative_point()
        folium.Marker(
            location=[centroid.y, centroid.x],
            icon=folium.DivIcon(
                html=f"""
                <div style="
                    font-family: 'Helvetica Neue', Arial, sans-serif;
                    font-size: 12px;
                    font-weight: 900;
                    color: #000000;
                    text-align: center;
                    white-space: nowrap;
                    transform: translate(-50%, -50%);
                    text-shadow: -2px -2px 0 #ffffff, 2px -2px 0 #ffffff, -2px 2px 0 #ffffff, 2px 2px 0 #ffffff,
                                 -1px -1px 0 #ffffff, 1px -1px 0 #ffffff, -1px 1px 0 #ffffff, 1px 1px 0 #ffffff;
                ">
                    {row['LGA']}
                </div>
                """
            )
        ).add_to(m)

    # --------------------------------------------------------------------------
    # Add Points layers from data/processed
    # --------------------------------------------------------------------------
    
    # 1. Add Conflict Point layer (from processed)
    print("Adding Conflict points from processed data...")
    df_conflict = pd.read_csv(conflict_csv)
    df_conflict = df_conflict.dropna(subset=["latitude", "longitude"])
    
    conflict_group = folium.FeatureGroup(name="Conflict", show=False)
    for idx, row in df_conflict.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=2.0, # Radius adjusted to 2.0
            color="#2563eb", # Blue
            fill=True,
            fill_color="#2563eb",
            fill_opacity=0.15, # Opacity adjusted for visibility
            weight=0,
            tooltip=f"Conflict Event (Date: {row.get('event_dates', 'Unknown')})"
        ).add_to(conflict_group)
    conflict_group.add_to(m)

    # 2. Add IDP Point layer (from processed)
    print("Adding IDP sites from processed data...")
    df_idp = pd.read_csv(idp_csv)
    df_idp = df_idp.dropna(subset=["latitude", "longitude"])
    
    idp_group = folium.FeatureGroup(name="IDPs", show=True)
    for idx, row in df_idp.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=3.5, # Radius adjusted to 3.5
            color="#9467bd", # Purple
            fill=True,
            fill_color="#9467bd",
            fill_opacity=0.45, # Opacity reduced to 0.45
            weight=0.4,
            edge_color="#ffffff",
            tooltip=f"IDP Site (Population: {int(row.get('idp_population', 0)):,})"
        ).add_to(idp_group)
    idp_group.add_to(m)

    # 3. Add Schools Point layer (from processed)
    print("Adding School points from processed data...")
    df_schools = pd.read_csv(schools_csv)
    df_schools = df_schools.dropna(subset=["latitude", "longitude"])
    
    schools_group = folium.FeatureGroup(name="Schools", show=True)
    for idx, row in df_schools.iterrows():
        status = row["status"]
        color = "#2ca02c" if status == "Open" else "#d62728" # Green vs Red
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=2.0, # Radius adjusted to 2.0
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.10, # Opacity reduced to 0.10
            weight=0.15,
            edge_color="#000000",
            tooltip=f"School in {row.get('lgs_names', 'Unknown')} ({status})",
            popup=folium.Popup(f"<b>School Status:</b> {status}", max_width=150)
        ).add_to(schools_group)
    schools_group.add_to(m)

    # Add Layer Control to map
    folium.LayerControl().add_to(m)

    # Add Custom HTML Legend
    legend_html = """
     <div style="position: fixed; 
                 bottom: 50px; left: 15px; width: 135px; height: auto; 
                 border: 1.5px solid #cccccc; z-index: 9999; font-size: 11px;
                 background-color: white;
                 opacity: 0.95;
                 padding: 8px;
                 font-family: 'Helvetica Neue', Arial, sans-serif;
                 border-radius: 4px;
                 box-shadow: 0 2px 4px rgba(0,0,0,0.15);">
     &nbsp;<b>Marker Legend</b><br>
     &nbsp;<i class="fa fa-circle fa-1x" style="color:#2ca02c"></i>&nbsp;&nbsp;Schools (Open)<br>
     &nbsp;<i class="fa fa-circle fa-1x" style="color:#d62728"></i>&nbsp;&nbsp;Schools (Closed)<br>
     &nbsp;<i class="fa fa-circle fa-1x" style="color:#9467bd"></i>&nbsp;&nbsp;IDPs (Purple)<br>
     &nbsp;<i class="fa fa-circle fa-1x" style="color:#2563eb"></i>&nbsp;&nbsp;Conflict (Blue)<br>
     </div>
     """
    m.get_root().html.add_child(folium.Element(legend_html))

    # Create State Boundaries for selection highlighting
    print("Creating state boundaries...")
    gdf_states = gdf_merged.dissolve(by="state").reset_index()

    # Add State Boundaries layer
    state_layer = folium.GeoJson(
        gdf_states,
        name="State Boundaries",
        style_function=lambda x: {
            "fillColor": "transparent",
            "color": "#4A5568",
            "weight": 1.5,
            "fillOpacity": 0.0
        },
        control=False,
        interactive=False
    )
    state_layer.add_to(m)

    # Add Custom JS for dynamic selection highlighting
    state_layer_name = state_layer.get_name()
    custom_js = f"""
    <script>
    window.highlightState = function(stateName) {{
        if (typeof {state_layer_name} !== 'undefined') {{
            {state_layer_name}.eachLayer(function(layer) {{
                var props = layer.feature.properties;
                if (stateName !== 'All' && props.state === stateName) {{
                    layer.setStyle({{
                        color: '#ff7e5f',
                        weight: 4.5,
                        fillColor: 'transparent',
                        fillOpacity: 0.0
                    }});
                    layer.bringToFront();
                }} else {{
                    layer.setStyle({{
                        color: '#4A5568',
                        weight: 1.5,
                        fillColor: 'transparent',
                        fillOpacity: 0.0
                    }});
                }}
            }});
        }}
    }};
    </script>
    """
    m.get_root().html.add_child(folium.Element(custom_js))

    # Save map
    m.save(output_map)
    m.save(output_map_disruption)
    print(f"Map saved successfully at {output_map} and {output_map_disruption}")

if __name__ == "__main__":
    create_map_processed()
