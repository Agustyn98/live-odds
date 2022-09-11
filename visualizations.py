# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

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


gauge = daq.Gauge(
    id="gauge",
    # scale={'start': 0, 'interval': 20, 'labelInterval': 1},
    scale={
        "custom": {
            10: {"style": {"fill": "tomato"}, "label": "Likely"},
            30: {"style": {"fill": "tomato"}, "label": "Leaning"},
            50: {"style": {"fill": "white"}, "label": "Draw"},
            70: {"style": {"fill": "lightskyblue"}, "label": "Leaning"},
            90: {"style": {"fill": "lightskyblue"}, "label": "Likely"},
        }
    },
    color={
        "gradient": True,
        "ranges": {"tomato": [0, 32], "white": [32, 68], "lightskyblue": [68, 100]},
    },
    value=ODDS1,
    label="",
    size=500,
    max=100,
    min=0,
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
            style={"text-align": "center", "padding": "1vw", "padding-bottom": "8vh"},
            id="descriptioin",
        ),
        gauge,
        html.H4("Timeline:", style={"text-align": "center", "padding-top": "8vh"}),
        dcc.Graph(
            id="example-graph",
            figure=fig,
            style={
                "text-align": "center",
                "padding-right": "6vw",
                "padding-left": "6vw",
                "padding-bottom": "3vw",
            },
        ),
        dcc.Interval(
            id="interval-component",
            interval=5 * 1000,
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
    ODDS_DRAW = df["draw_odds"].iloc[-1]
    ODDS2 = df["team2_odds"].iloc[-1]
    print(df.to_string())
    fig = px.bar(
        df,
        x="time",
        y=["team1_odds", "draw_odds", "team2_odds"],
        color_discrete_map={
            "team1_odds": "tomato",
            "draw_odds": "palegreen",
            "team2_odds": "lightskyblue",
        },
        template=templates[0],
    ).update_layout(yaxis_title="Odds")

    series_names = [TEAM1, "Draw", TEAM2]

    for idx, name in enumerate(series_names):
        fig.data[idx].name = name

    SCORE1 = df["team1_score"].iloc[-1]
    SCORE2 = df["team2_score"].iloc[-1]
    children = f"🔴 {TEAM1} {SCORE1} - {SCORE2} {TEAM2} 🔵"

    if ODDS1 >= ODDS2 and ODDS1 > ODDS_DRAW:
        chance = 33 - (ODDS1 - 34) / 2
        label_text = f"{TEAM1} Wins"
    elif ODDS2 > ODDS_DRAW:
        chance = 67 + (ODDS2 - 34) / 2
        label_text = f"{TEAM2} Wins"
    else:
        chance = 50 + (ODDS2 / 3 - ODDS1 / 3) * 1.2
        label_text = f"Toss-up/Draw"


    return fig, chance, label_text, children


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")


# TODO:
# Make gauge mobile friendly, or not
# create bq view
# replace csv with bigquery view
# Test scaling of gauge with real matches
# handle match-end, betting ending, etc
