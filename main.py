import sys
from pathlib import Path

import ezdxf
from ezdxf.document import Drawing
from shapely import Polygon
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
    polylines = []
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
            texts.append(item)

    gpd.GeoSeries(polygons).to_file(input_path.with_suffix('.gpkg'))


if __name__ == '__main__':
    file_path = Path('sample_data/polygons_1.dxf')
    main(file_path)
