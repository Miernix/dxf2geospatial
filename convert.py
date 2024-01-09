from pathlib import Path
from typing import Optional

import geopandas as gpd
import typer

from tools import load_file
from tools.polygon import (cad_polygons_to_shapely,
                           get_all_polygons,
                           match_text_to_polygon)
from tools.text import get_all_texts

app = typer.Typer()


def extract_polygons(input_path: Path,
                     output_path: Path):
    doc = load_file(input_path)
    msp = doc.modelspace()

    # get all suitable objects
    cad_polygons = get_all_polygons(msp)

    # convert CAD polygons (LWPOLYLINES) to shapely polygons
    geospatial_polygons = cad_polygons_to_shapely(cad_polygons=cad_polygons)

    # get all text objects
    texts = get_all_texts(msp)
    texts_df = gpd.GeoDataFrame(data=texts, geometry='geom')

    # match point to a polygon
    result_df = match_text_to_polygon(polygons=geospatial_polygons,
                                      texts_df=texts_df)

    result_df.to_file(str(output_path))


@app.command()
def main(input_path: Path,
         output_path: Optional[Path] = None):

    if not output_path:
        output_path = input_path.with_suffix('.gpkg')

    extract_polygons(input_path=input_path,
                     output_path=output_path)


if __name__ == '__main__':
    app()
