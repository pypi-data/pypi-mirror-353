import dataclasses
import rich
import rich.console
import rich.table
import rich.layout
import rich.text
import math
from typing import Callable, Iterable, Generic, Optional, TypeVar

R = TypeVar("R")
C = TypeVar("C")


@dataclasses.dataclass
class HeatmapCell(Generic[R, C]):
    """Contains the data for a single cell in the heatmap.

    If text is present, it will be colored and printed on the
    default background. If text is absent, the entire cell will
    be filled with color.

    Attributes:
        row: The value of the row that this cell is in.
        col: The value of the column that this cell is in.
        value: This cell's value. This will be used to compute the
            cell's color.
        text: If set, the string to print."""

    row: R
    col: C
    value: float
    text: Optional[str] = None


def _default_colormap(value: float):
    return rich.color.Color.from_rgb(
        255 * value,
        0,
        0,
    )


class Heatmap(rich.table.Table, Generic[R, C]):
    """A rich-renderable heatmap object."""

    def __init__(
        self,
        cells: Iterable[HeatmapCell[R, C]],
        show_header: bool = True,
        cell_width: Optional[int] = None,
        cell_padding: Optional[int] = None,
        colormap: Callable[[float], rich.color.Color] = _default_colormap,
    ):
        """Initializes the Heatmap object.

        Args:
            cells: A collection of HeatmapCells that this heatmap will
                render.
            show_header: If True, add axes at the top and left to show
                the values in the heatmap's domain.
            cell_width: If set, set the width of each column to this value. If
                unset, column widths will be automatically obtained from cell
                contents.
            cell_padding: If set, add extra horizontal padding between cells. If
                unset, cells will be directly adjacent with each other.
            colormap: A callable that maps floats in [0, 1] to rich Color
                objects for rendering. Cell values will be normalized linearly
                into [0, 1] before being passed to the colormap.
        """
        self._cells = {(c.row, c.col): c for c in cells}
        self._show_header = show_header
        self._cell_width = cell_width
        self._cell_spacing = cell_padding
        self._colormap = colormap

    def _row_values(self) -> list[R]:
        """Sorted list of distinct row values for all cells in the map."""
        return list(sorted({hc.row for hc in self._cells.values()}))

    def _col_values(self) -> list[C]:
        """Sorted list of distinct col values for all cells in the map."""
        return list(sorted({hc.col for hc in self._cells.values()}))

    def _min_value(self) -> float:
        """Minimum value over all cells in the map"""
        return min((hc.value for hc in self._cells.values()), default=0)

    def _max_value(self) -> float:
        """Maximum value over all cells in the map"""
        return max((hc.value for hc in self._cells.values()), default=math.inf)

    def __rich__(self) -> rich.table.Table:
        spc = self._cell_spacing if self._cell_spacing is not None else 0

        tab = rich.table.Table(box=None, padding=(0, spc, 0, 0), show_header=False)

        if self._show_header:
            tab.add_column(
                "", style="bold", justify="center", no_wrap=True, width=self._cell_width
            )

        for col_value in self._col_values():
            tab.add_column(
                str(col_value), justify="right", no_wrap=True, width=self._cell_width
            )

        if self._show_header:
            strs = [str(cv) for cv in self._col_values()]
            tab.add_row("", *strs)

        min_value = self._min_value()
        max_value = self._max_value()

        for row_value in self._row_values():
            strs = []
            if self._show_header:
                strs.append(str(row_value))
            for col_value in self._col_values():
                if (row_value, col_value) in self._cells:
                    cell = self._cells[row_value, col_value]
                    scale = (cell.value - min_value) / (max_value - min_value)
                    color = self._colormap(scale)
                    if cell.text is None:
                        style = rich.style.Style(color=color, bgcolor=color)
                        text = "█" * (self._cell_width or 1)
                    else:
                        style = rich.style.Style(color=color)
                        text = cell.text
                    strs.append(rich.text.Text(text, style))
                else:
                    strs.append("")
            tab.add_row(*strs)

        return tab
