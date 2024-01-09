from pathlib import Path
from typing import Optional

import typer

from actions import match_label_to_closed_polyline

app = typer.Typer()


@app.command()
def main(input_path: Path,
         output_path: Optional[Path] = None):
    if not output_path:
        output_path = input_path.with_suffix('.gpkg')

    # trigger processing
    result_df = match_label_to_closed_polyline(input_path=input_path)

    result_df.to_file(str(output_path))


if __name__ == '__main__':
    app()
