# -*- coding: utf-8 -*-

""" Functions to provide analysis for the synthetic control method. """

import numpy as np
import plotly.graph_objects as go
from plotly.colors import DEFAULT_PLOTLY_COLORS


def compare_to_synthetic_control(
    y,
    y_pred_ci,
    treatment_start,
    treatment_end=None,
    treatment_name="Treatment",
    y_axis="Value",
):
    """Display a comparison between the treatment group and the synthetic control group.

    Parameters
    ----------
    y : pandas.Series
        The treatment group.
    y_pred_ci : pandas.DataFrame
        The synthetic control group.
    treatment_start : datetime
        The start of the treatment period.
    treatment_end : datetime
        The end of the treatment period.

    Returns
    -------
    fig : plotly.graph_objects.Figure
        The plotly figure showing the comparison between the treatment group and the
        synthetic control group.
    """
    data = get_plot_data(y, y_pred_ci, treatment_name)
    layout = get_plot_layout(y_axis)
    fig = go.Figure(data=data, layout=layout)
    fig = add_treatment_period(fig, treatment_start, treatment_end)
    return fig


def get_plot_data(y, y_pred_ci, treatment_name):
    """Create the plotly data for the comparison plot between the treatment group
    and the synthetic control group, including the confidence intervals.

    Parameters
    ----------
    y : pandas.Series
        The actual value of the metric for the treatment group.
    y_pred_ci : pandas.DataFrame
        The predicted values for each percentile for the synthetic control group.
    treatment_name : str
        The name of the treatment group.

    Returns
    -------
    data : list
        The list of plotly data objects to display the comparison between the
        treatment group and the synthetic control group.
    """
    treatment_color = DEFAULT_PLOTLY_COLORS[0]
    control_color = DEFAULT_PLOTLY_COLORS[1]
    y_pred = get_baseline_prediction(y_pred_ci)
    data = [
        go.Scatter(
            x=y.index,
            y=y,
            name=treatment_name,
            line_color=treatment_color,
            line_width=5,
        ),
        go.Scatter(
            x=y.index,
            y=y_pred,
            name="Synthetic Control",
            line_color=control_color,
            line_width=5,
        ),
    ]
    data += add_confidence_interval(y_pred_ci, control_color)
    return data


def get_baseline_prediction(y_pred_ci):
    """Return the baseline prediction for the synthetic control group. The baseline
    prediction is the prediction for the 50th percentile if available, or the average
    of the predictions for all percentiles otherwise.

    Parameters
    ----------
    y_pred_ci : pandas.DataFrame
        The predicted values for each percentile for the synthetic control group.

    Returns
    -------
    y_pred : pandas.Series
        The baseline prediction for the synthetic control group.
    """
    if 50 in y_pred_ci:
        y_pred = y_pred_ci[50]
    else:
        y_pred = y_pred_ci.mean(axis=1)
    return y_pred


def add_confidence_interval(y_pred_ci, color):
    """Add the confidence interval to the plotly data.

    Parameters
    ----------
    y_pred_ci : pandas.DataFrame
        The predicted values for each percentile for the synthetic control group.
    color : str
        The color to use for the synthetic control group.

    Returns
    -------
    ci_data : list
        The list of plotly data objects to display the confidence interval.
    """
    min_ci = y_pred_ci.columns.min()
    max_ci = y_pred_ci.columns.max()
    ci_range = max_ci - min_ci
    color = get_opacity_color(color)
    columns = y_pred_ci.columns.sort_values(
        key=lambda x: np.abs(50 - x), ascending=False
    )
    ci_data = []
    for i, col in enumerate(columns):
        ci_data.append(
            go.Scatter(
                x=y_pred_ci.index,
                y=y_pred_ci[col],
                name=f"{ci_range}% confidence interval",
                fill="tonexty",
                line_color=color,
                fillcolor=color,
                showlegend=i == 0,
                legendgroup="CI",
            )
        )
    return ci_data


def get_opacity_color(color, opacity=0.1):
    """Return the color with the specified opacity.

    Parameters
    ----------
    color : str
        A color in rgb string format.
    opacity : float
        The opacity to apply to the color.

    Returns
    -------
    color : str
        The color with the specified opacity.
    """
    return color.replace("rgb", "rgba").replace(")", f", {opacity})")


def add_treatment_period(fig, treatment_start, treatment_end):
    """Add vertical lines to the plotly figure to delimitate the treatment period.

    Parameters
    ----------
    fig : plotly.graph_objects.Figure
        The plotly figure to add the vertical lines to.
    treatment_start : datetime
        The start of the treatment period.
    treatment_end : datetime
        The end of the treatment period.

    Returns
    -------
    fig : plotly.graph_objects.Figure
        The plotly figure with the vertical lines added.
    """
    fig.add_vline(
        x=treatment_start.timestamp() * 1000,
        line_color="black",
        line_dash="dash",
        annotation={"text": "Treatment Start", "xanchor": "center", "y": 1.1},
    )
    if treatment_end:
        fig.add_vline(
            x=treatment_end.timestamp() * 1000,
            line_color="black",
            line_dash="dash",
            annotation={"text": "Treatment End", "xanchor": "center", "y": 1.1},
        )
    return fig


def get_plot_layout(y_axis):
    """Return the plotly layout for the comparison plot between the treatment group
    and the synthetic control group.

    Parameters
    ----------
    y_axis : str
        The label for the y-axis.

    Returns
    -------
    layout : plotly.graph_objects.Layout
        The plotly layout for the comparison plot between the treatment group and the
        synthetic control group.
    """
    layout = go.Layout(
        xaxis={"title": "Date"}, yaxis={"title": y_axis}, template="none"
    )
    return layout
