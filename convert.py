import sys
from pathlib import Path
from typing import List, Optional

import ezdxf
import typer
from ezdxf.document import Drawing
from ezdxf.entities import LWPolyline
from shapely import Polygon, Point
import geopandas as gpd

app = typer.Typer()


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


def get_all_texts(msp) -> List:
    texts = []
    for item in msp:
        if item.dxf.dxftype == 'TEXT':
            coords = list(item.get_placement()[1])[0:2]
            row = {'text': item.dxf.text, 'geom': Point(coords)}
            texts.append(row)
    return texts


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


@app.command()
def main(input_path: Path,
         output_path: Optional[Path] = None):
    # load the dxf drawing
    doc = load_file(input_path)
    msp = doc.modelspace()

    # get all suitable objects
    cad_polygons = get_all_polygons(msp)

    # convert CAD polygons (LWPOLYLINES) to shapely polygons
    geospatial_polygons = cad_polygons_to_shapely(cad_polygons)

    # get all text objects
    texts = get_all_texts(msp)
    texts_df = gpd.GeoDataFrame(texts, geometry='geom')

    # match point to a polygon
    result_df = match_text_to_polygon(polygons=geospatial_polygons,
                                      texts_df=texts_df)

    if not output_path:
        output_path = input_path.with_suffix('.gpkg')

    result_df.to_file(str(output_path))


if __name__ == '__main__':
    app()
