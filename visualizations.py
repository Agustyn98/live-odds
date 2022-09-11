# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from tkinter.ttk import Style
from dash import Dash, html, dcc
import plotly.express as px
import dash_daq as daq
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template


import pandas as pd

app = Dash(
    __name__,
    assets_folder="assets",
    include_assets_files=True,
    external_stylesheets=[dbc.themes.DARKLY],
)

templates = [
    "darkly",
]
load_figure_template(templates)


df = pd.read_csv("../data.csv")

TEAM1 = df["team1"].iloc[-1]
TEAM2 = df["team2"].iloc[-1]
SCORE1 = df["team1_score"].iloc[-1]
SCORE2 = df["team2_score"].iloc[-1]
ODDS1 = df["team1_odds"].iloc[-1]


print(df.to_string())

fig = px.bar(
    df,
    x="time",
    y=["team1_odds", "draw_odds", "team2_odds"],
)

if ODDS1 < 34:
    label_text = f"{TEAM2} Wins"
elif ODDS1 >= 34 and ODDS1 < 67:
    label_text = f"Toss-up"
else:
    label_text = f"{TEAM1} Wins"


gauge = daq.Gauge(
    id="gauge",
    color={
        "gradient": True,
        "ranges": {"tomato": [0, 32], "white": [32, 68], "lightskyblue": [68, 100]},
    },
    value=ODDS1,
    label=label_text,
    size=500,
    max=100,
    min=0,
    units="asd"
)


app.layout = html.Div(
    children=[
        html.H1(
            id="score",
            children=f"{TEAM1} {SCORE1} - {SCORE2} {TEAM2}",
            style={"text-align": "center", "padding-top": "2vh"},
        ),
        html.H3(
            "Live result forecast based on betting odds",
            style={"text-align": "center", "padding": "1vh", "padding-bottom": "8vh"},
            id="descriptioin",
        ),
        gauge,
        html.H4("Timeline:", style={"text-align": "center", "padding-top": "8vh"}),
        dcc.Graph(
            id="example-graph",
            figure=fig,
            style={"text-align": "center", "padding-right": "6vw", "padding-left": "6vw", "padding-bottom": "3vw"},
        ),
        dcc.Interval(
            id="interval-component",
            interval=7 * 1000,
            n_intervals=0, 
        ),
    ]
)


@app.callback(
    Output("example-graph", "figure"),
    Output("gauge", "value"),
    Output("gauge", "label"),
    Output("score", "children"),
    Input("interval-component", "n_intervals"),
)
def update_metrics(n=0):
    df = pd.read_csv("../data.csv")
    TEAM1 = df["team1"].iloc[-1]
    TEAM2 = df["team2"].iloc[-1]
    ODDS1 = df["team1_odds"].iloc[-1]
    print(df.to_string())
    fig = px.bar(
        df,
        x="time",
        y=["team1_odds", "draw_odds", "team2_odds"],
        color_discrete_map={"team1_odds": "tomato", "draw_odds": "palegreen", "team2_odds": "lightskyblue"},
        template=templates[0],
    ).update_layout(yaxis_title="Odds")

    series_names = [TEAM1, "Draw", TEAM2]

    for idx, name in enumerate(series_names):
        fig.data[idx].name = name
        fig.data[idx].hovertemplate = name

    SCORE1 = df["team1_score"].iloc[-1]
    SCORE2 = df["team2_score"].iloc[-1]
    children = f"{TEAM1} {SCORE1} - {SCORE2} {TEAM2}"

    if ODDS1 < 37:
        label_text = f"{TEAM2} Wins"
    elif ODDS1 >= 37 and ODDS1 <= 63:
        label_text = f"Toss-up"
    else:
        label_text = f"{TEAM1} Wins"

    return fig, ODDS1, label_text, children


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")


# TODO:
# Make gauge mobile friendly, or not
# better colors, lighter red and blue
# Better " X wins" msg
# create bq view
# replace csv with bigquery view
