"""
Visualization package for SocialMapper.

This package contains modules for generating visualizations of community resources and demographics.
"""

# Import and re-export all public functions
from .map_utils import get_variable_label
from .single_map import generate_map, generate_isochrone_map
from .panel_map import generate_paneled_isochrone_map, generate_paneled_census_map
from .generate_maps import generate_maps_for_variables
# Folium imports removed - migrated to Plotly
from .plotly_map import (
    create_plotly_map,
    create_plotly_map_for_streamlit,
    generate_plotly_maps_for_variables
)

__all__ = [
    'get_variable_label',
    'generate_map',
    'generate_isochrone_map',
    'generate_paneled_isochrone_map',
    'generate_paneled_census_map',
    'generate_maps_for_variables',
    # Folium functions removed - migrated to Plotly
    'create_plotly_map',
    'create_plotly_map_for_streamlit',
    'generate_plotly_maps_for_variables'
] 