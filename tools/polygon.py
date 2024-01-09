from typing import List, Optional

from ezdxf.entities import LWPolyline
from shapely import Polygon
import geopandas as gpd


def get_all_polygons(modelspace) -> List[Optional[LWPolyline]]:
    polygons = []
    for item in modelspace:
        if item.dxf.dxftype == 'LWPOLYLINE' and item.is_closed and not item.has_arc:
            polygons.append(item)

    return polygons


def cad_polygons_to_shapely(cad_polygons: List) -> List[Polygon]:
    geospatial_polygons = []
    for polyline in cad_polygons:
        with polyline.points("xy") as vertices:
            geospatial_polygons.append(Polygon(vertices))

    return geospatial_polygons


def match_text_to_polygon(polygons: List[Polygon],
                          texts_df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    result_df = []
    for polygon in polygons:
        matched_bool = texts_df.intersects(polygon)
        if sum(matched_bool) != 1:
            continue
            # todo: handle this
        result_row = {'annotation': texts_df.iloc[0]['text'],
                      'geom': polygon}
        result_df.append(result_row)
    result_df = gpd.GeoDataFrame(result_df, geometry='geom')
    return result_df
