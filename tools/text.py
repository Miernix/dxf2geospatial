from typing import List

from shapely import Point


def get_all_texts(msp) -> List:
    texts = []
    for item in msp:
        if item.dxf.dxftype == 'TEXT':
            coords = list(item.get_placement()[1])[0:2]
            row = {'text': item.dxf.text,
                   'geom': Point(coords)}
            texts.append(row)
    return texts
