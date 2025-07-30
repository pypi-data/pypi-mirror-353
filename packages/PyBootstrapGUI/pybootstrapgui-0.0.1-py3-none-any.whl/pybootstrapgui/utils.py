from pathlib import Path
from shutil import copytree


def copy_bootstrap_static_to(dest: str):
    """copy_bootstrap_static_to(str(Path(__file__).parent.absolute() / "static")"""
    static_path = str(Path(__file__).parent.absolute() / "static")
    copytree(static_path, dest, dirs_exist_ok=True)


class B:
    """
    Bootstrap screen breakpoints
    """

    XS = "xs"
    SM = "sm"
    MD = "md"
    LG = "lg"
    XL = "xl"
    XXL = "xxl"


class D:
    """
    Display utilities
    """

    NONE = "d-none"
    INLINE = "d-inline"
    INLINE_BLOCK = "d-inline-block"
    BLOCK = "d-block"
    GRID = "d-grid"
    TABLE = "d-table"
    TABLE_CELL = "d-table-cell"
    TABLE_ROW = "d-table-row"
    FLEX = "d-flex"
    INLINE_FLEX = "d-inline-flex"


class V:
    """
    Vertical alignment for flexbox
    """

    START = "justify-content-start"
    END = "justify-content-end"
    CENTER = "justify-content-center"
    BETWEEN = "justify-content-between"
    AROUND = "justify-content-around"
    EVENLY = "justify-content-evenly"


class H:
    """
    Horizontal alignment for flexbox
    """

    START = "align-items-start"
    END = "align-items-end"
    CENTER = "align-items-center" # Alternative "text-center"
    BASELINE = "align-items-baseline"
    STRETCH = "align-items-stretch"


class C:
    """
    Bootstrap colors
    """

    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    DANGER = "danger"
    WARNING = "warning"
    INFO = "info"
    LIGHT = "light"
    DARK = "dark"

    LINK = "link"


class R:
    """
    Bootstrap border radius
    size and type can be mixed like "rounded-top-2"
    """

    ROUNDED = "rounded"
    ROUNDED_TOP = "rounded-top"
    ROUNDED_END = "rounded-end"
    ROUNDED_BOTTOM = "rounded-bottom"
    ROUNDED_START = "rounded-start"
    ROUNDED_CIRCLE = "rounded-circle"
    ROUNDED_PILL = "rounded-pill"
    ROUNDED_0 = "rounded-0"
    ROUNDED_1 = "rounded-1"
    ROUNDED_2 = "rounded-2"
    ROUNDED_3 = "rounded-3"
    ROUNDED_4 = "rounded-4"
    ROUNDED_5 = "rounded-5"
