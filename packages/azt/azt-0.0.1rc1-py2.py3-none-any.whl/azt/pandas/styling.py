# azt/pandas/styling.py

"""
azt.pandas.styling
Pandas-centric styling helpers.
"""
from __future__ import annotations
import pandas as _pd      # local import keeps azt import-time light

def highlight_columns(
        df: _pd.DataFrame | _pd.io.formats.style.Styler,
        columns=None,
        bg_color: str = "#FFF2AB",
        *,
        value_color: bool = False,
) -> _pd.io.formats.style.Styler:
    """Return a Styler that highlights *columns* (see docstring earlier)."""
    styler = df.style if isinstance(df, _pd.DataFrame) else df

    if columns is None:
        base = styler.data if hasattr(styler, "data") else df
        columns = [base.columns[-1]]
    elif isinstance(columns, str):
        columns = [columns]

    styler = styler.set_properties(subset=columns,
                                   **{"background-color": bg_color})

    if value_color:
        styler = styler.applymap(
            lambda v: "color:green" if v > 0 else "color:red",
            subset=columns,
        )
    return styler
