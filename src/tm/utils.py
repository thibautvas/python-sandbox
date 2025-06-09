from typing import List, Optional, Union

import pandas as pd
import plotly.graph_objects as go

pd.options.display.notebook_repr_html = False  # preserve monospaced font


def format_args(args: dict, inplace: bool = True) -> Optional[dict]:
    """
    format args to pass to an sql query
    """
    target = args if inplace else args.copy()
    for k, v in target.items():
        target[k] = str(v).replace("[", "").replace("]", "")
    return target if not inplace else None


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
