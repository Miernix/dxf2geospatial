from pathlib import Path
from typing import Optional

import geopandas as gpd
import pandas as pd

from tools import load_file
from tools.polygon import (get_all_polygons,
                           cad_polygons_to_shapely,
                           match_text_to_polygon)
from tools.text import get_texts_with_positions


def match_label_to_closed_polyline(input_path: Path,
                                   existing_df: Optional[gpd.GeoDataFrame] = None):
    doc = load_file(input_path)
    msp = doc.modelspace()

    # get all suitable objects
    cad_polygons = get_all_polygons(msp)

    # convert CAD polygons (LWPOLYLINES) to shapely polygons
    geospatial_polygons = cad_polygons_to_shapely(cad_polygons=cad_polygons)

    # get all text objects
    texts = get_texts_with_positions(msp)
    texts_df = gpd.GeoDataFrame(data=texts, geometry='geom')

    # match point to a polygon
    matched_df = match_text_to_polygon(polygons=geospatial_polygons,
                                       texts_df=texts_df)

    if existing_df:
        matched_df = pd.concat([existing_df, matched_df])

    return matched_df
