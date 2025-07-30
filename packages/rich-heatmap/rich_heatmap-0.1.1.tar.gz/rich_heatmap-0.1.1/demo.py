import noise
import click
from rich import print
import matplotlib
import rich
import itertools
import cmasher  # noqa: F401

from rich_heatmap import heatmap


@click.command
@click.option("--numbers/--no-numbers", type=bool, default=False)
@click.option(
    "--colormap", type=click.Choice(matplotlib.colormaps), default="cmr.ember"
)
def main(numbers: bool, colormap: str):
    cmap = matplotlib.colormaps[colormap]

    def colormap_fun(value: float) -> tuple[float, float, float]:
        rgba = cmap(value)
        return rich.color.Color.from_rgb(
            255 * rgba[0],
            255 * rgba[1],
            255 * rgba[2],
        )

    cells = []
    for row, col in itertools.product(range(30), range(20)):
        value = noise.snoise2(col / 10, row / 15)
        cells.append(
            heatmap.HeatmapCell(row, col, value, f"{value:0.1f}" if numbers else None)
        )

    print(
        heatmap.Heatmap(
            cells=cells,
            show_header=True,
            cell_width=None if numbers else 3,
            cell_padding=1 if numbers else None,
            colormap=colormap_fun,
        )
    )


if __name__ == "__main__":
    main()
