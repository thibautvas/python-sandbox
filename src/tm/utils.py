import re
from typing import Dict, List, Optional, Union

import pandas as pd
import plotly.graph_objects as go


def format_args(
    args: Dict[str, Union[int, str, List[int], List[str]]],
) -> Dict[str, Union[int, str]]:
    """
    format args to pass to sql queries
    convert list values to comma-separated strings
    convert string values to quoted strings
    """
    args_out = args.copy()
    for k, v in args.items():
        if isinstance(v, list):
            args_out[k] = re.sub(r"[\[\]]", "", str(v))
        elif isinstance(v, str):
            args_out[k] = f"'{v}'"
    return args_out


def ts_plot(
    df: pd.DataFrame,
    y: Union[str, List[str]],
    x: str = "day",
    hue: Optional[str] = None,
) -> None:
    """
    plot a line graph using plotly.graph_objects
    """
    fig = go.Figure()

    if isinstance(y, str):
        y = [y]

    if hue:
        for group_name, group_df in df.groupby(hue):
            for y_col in y:
                fig.add_trace(
                    go.Scatter(
                        x=group_df[x],
                        y=group_df[y_col],
                        mode="lines",
                        name=f"{group_name}: {y_col}"
                        if len(y) > 1
                        else str(group_name),
                    )
                )
    else:
        for y_col in y:
            fig.add_trace(go.Scatter(x=df[x], y=df[y_col], mode="lines", name=y_col))

    fig.update_layout(
        title=f"{', '.join(y)} per {x}",
        template="plotly_dark",
    )
    fig.show()
