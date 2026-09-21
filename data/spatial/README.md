# Spatial Data & Grid Cartography

This directory contains geospatial boundary layers and electrical infrastructure coordinates for the Colombian Caribbean.

## Tracking & Storage Rules
* Large GeoPackages (`*.gpkg`) and GeoJSONs (`*.geojson`) are tracked via **Git LFS** (`data/spatial/*.gpkg`, `data/spatial/*.geojson`).
* Lightweight service catalogs and CSV listings are tracked as standard Git text files.

## Files:
* `mgn_caribe_municipios.gpkg`: Cleaned, reprojected boundaries (EPSG:4326 / EPSG:9377) for the 7 Caribbean departments (Atlántico, Bolívar, Cesar, Córdoba, La Guajira, Magdalena, Sucre) from DANE MGN 2023.
* `upme/`: ArcGIS service discovery metadata, medium-voltage distribution circuit traces, and substation coordinates for Afinia and Air-e.
