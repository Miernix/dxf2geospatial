import sys
from pathlib import Path

import ezdxf
from ezdxf.document import Drawing


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
