"""Utility functions for exploratory data analysis.

This module provides:
- format_args: format args to pass to sql queries.
- ts_plot: timeseries plot using plotly.graph_objects.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def format_args(
    args: dict[str, int | str | list[int] | list[str]],
) -> dict[str, int | str]:
    """Format args to pass to sql queries.

    Convert list values to comma-separated strings.
    Convert string values to quoted strings.
    """
    args_out = args.copy()
    for key, value in args_out.items():
        if isinstance(value, list):
            args_out[key] = ", ".join([str(element) for element in value])
    return args_out


def _arg_to_list(arg: str | list[str] | None) -> list[str]:
    """Transform arg passed as string or None to list of strings."""
    if isinstance(arg, list):
        arg_out = arg.copy()
    elif isinstance(arg, str):
        arg_out = [arg]
    else:
        arg_out = []
    return arg_out


def ts_plot(
    df: pd.DataFrame,
    y: str | list[str],
    x: str = "day",
    hue: str | list[str] | None = None,
    secondary_y: str | list[str] | None = None,
) -> go.Figure:
    """Plot a timeseries as a line graph using plotly.graph_objects.

    Args:
        df: Data to plot.
        y: Column(s) to use as y-axis values.
        x: Column to use as the x-axis (default "day").
        hue: Column(s) to group lines by (default []).
        secondary_y: Column(s) to plot on the secondary y-axis (default []).

    Returns:
        go.Figure: A Plotly Figure object containing the line plot.

    """
    # consistent typing
    y_list = _arg_to_list(y)
    hue_list = _arg_to_list(hue)
    secondary_y_list = _arg_to_list(secondary_y)

    # validate parameters
    for col in [x, *y_list, *hue_list, *secondary_y_list]:
        if col not in df.columns:
            error_message = f"Column {col} not found in DataFrame."
            raise ValueError(error_message)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    df_plot = df.groupby([x, *hue_list])[y_list].sum().reset_index()
    group_cols = hue_list if hue_list else [lambda _: ""]
    for group_name, df_group in df_plot.groupby(group_cols):
        for y_col in y_list:
            fig.add_trace(
                go.Scatter(
                    x=df_group[x],
                    y=df_group[y_col],
                    mode="lines",
                    name=(
                        f"{', '.join(group_name) + ': ' if group_name != ('',) else ''}"
                        f"{y_col}"
                    )
                    if len(y_list) > 1
                    else f"{', '.join(group_name)}",
                ),
                secondary_y=(y_col in secondary_y_list),
            )

    fig.update_layout(
        title=f"{', '.join(y_list)} per {x}",
        template="plotly_dark",
    )

    return fig
