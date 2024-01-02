import sys
from pathlib import Path
from typing import List, Optional

import ezdxf
from ezdxf.document import Drawing
from ezdxf.entities import LWPolyline
from shapely import Polygon, Point
import geopandas as gpd


def load_file(path: Path) -> Drawing:
    try:
        doc = ezdxf.readfile(path)
    except IOError:
        print(f"Not a DXF file or a generic I/O error.")
        sys.exit(1)
    except ezdxf.DXFStructureError:
        print(f"Invalid or corrupted DXF file.")
        sys.exit(2)

    return doc


def main(input_path: Path):
    # load the dxf drawing
    doc = load_file(input_path)
    msp = doc.modelspace()

    # get all polylines objects
    polylines: List[Optional[LWPolyline]] = []
    for item in msp:
        if item.dxf.dxftype == 'LWPOLYLINE':
            polylines.append(item)

    # convert polylines to shapely polygons if possible
    polygons = []
    for polyline in polylines:
        if polyline.is_closed and not polyline.has_arc:
            with polyline.points("xy") as vertices:
                polygon = Polygon(vertices)
                polygons.append(polygon)

    # get all text objects
    texts = []
    for item in msp:
        if item.dxf.dxftype == 'TEXT':
            coords = list(item.get_placement()[1])[0:2]
            row = {'text': item.dxf.text, 'geom': Point(coords)}
            texts.append(row)
    texts_df = gpd.GeoDataFrame(texts, geometry='geom')

    # match point to a polygon
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

    result_df.to_file(str(input_path.with_suffix('.gpkg')))


if __name__ == '__main__':
    file_path = Path('sample_data/polygons_1.dxf')
    main(file_path)
