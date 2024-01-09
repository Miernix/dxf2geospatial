from typing import List, Dict

from ezdxf.entities import Text
from ezdxf.layouts import Modelspace
from shapely import Point


def get_texts_with_positions(msp: Modelspace) -> List[Dict[str, Point]]:
    texts = []
    for item in msp:
        item: Text
        if item.dxf.dxftype == 'TEXT':
            coords = list(item.get_placement()[1])[0:2]
            row = {'text': item.dxf.text,
                   'geom': Point(coords)}
            texts.append(row)
    return texts

