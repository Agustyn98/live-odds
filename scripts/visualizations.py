from time import sleep
from dash import Dash, html, dcc
import plotly.express as px
import dash_daq as daq
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from google.cloud import bigquery
import os
from flask_caching import Cache

app = Dash(
    __name__,
    assets_folder="../assets",
    include_assets_files=True,
    external_stylesheets=[dbc.themes.DARKLY],
)

cache = Cache(
    app.server,
    config={
        "CACHE_TYPE": "filesystem",
        "CACHE_DIR": "cache-directory",
    },
)

TIMEOUT = 48

TEAM1 = os.environ["TEAM1"]
TEAM2 = os.environ["TEAM2"]
project_id = "marine-bison-360321"
os.environ["GCLOUD_PROJECT"] = project_id

client = bigquery.Client()

sql = f"""
    SELECT * FROM `marine-bison-360321.betting_dataset.view_formatted`
    WHERE
    LOWER(team1) LIKE "%{TEAM1}%"
    AND LOWER(team2) LIKE "%{TEAM2}%"
    """

templates = ["darkly"]
load_figure_template(templates)


@cache.memoize(timeout=TIMEOUT)
def get_data():
    print("RUNNING EXPENSIVE QUERY !\n")
    df = client.query(sql, project=project_id).to_dataframe()
    i = 0
    while len(df) <= 0:
        if i >= 3:
            quit("ERROR: No data returned from query.")
        i += 1
        print("No data return from query, retrying in 5 seconds...")
        sleep(5)
        df = client.query(sql, project=project_id).to_dataframe()

    return df


# df = pd.read_csv("../../data.csv")
df = get_data()
print(df)

TEAM1 = df["team1"].iloc[-1]
TEAM2 = df["team2"].iloc[-1]
SCORE1 = df["team1_score"].iloc[-1]
SCORE2 = df["team2_score"].iloc[-1]
ODDS1 = df["team1_odds"].iloc[-1]


fig = px.bar(
    df,
    x="time",
    y=["team1_odds", "draw_odds", "team2_odds"],
)


gauge = daq.Gauge(
    id="gauge",
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
    label="Live result forecast based on betting odds",
    size=600,
    max=100,
    min=0,
)


app.layout = html.Div(
    children=[
        html.H1(
            id="score",
            children=f"{TEAM1} {SCORE1} - {SCORE2} {TEAM2}",
            style={
                "text-align": "center",
                "padding-top": "1vh",
                "padding-bottom": "1vh",
            },
        ),
        gauge,
        html.H3(id="probability", children=""),
        html.H4("Timeline:", style={"text-align": "center", "padding-top": "2vh"}),
        dcc.Graph(
            id="example-graph",
            figure=fig,
            style={
                "text-align": "center",
                "padding-right": "2vw",
                "padding-left": "2vw",
                "padding-bottom": "2vw",
            },
        ),
        dcc.Interval(
            id="interval-component",
            interval=50 * 1000,
            n_intervals=0,
        ),
    ]
)


@app.callback(
    Output("example-graph", "figure"),
    Output("gauge", "value"),
    Output("score", "children"),
    Output("probability", "children"),
    Input("interval-component", "n_intervals"),
)
def update_metrics(n=0):
    # df = pd.read_csv("../../data.csv")
    df = get_data()
    TEAM1 = df["team1"].iloc[-1]
    TEAM2 = df["team2"].iloc[-1]
    ODDS1 = df["team1_odds"].iloc[-1]
    ODDS_DRAW = df["draw_odds"].iloc[-1]
    ODDS2 = df["team2_odds"].iloc[-1]

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

    if ODDS1 > ODDS2 and ODDS1 > ODDS_DRAW:
        chance = 33 - (ODDS1 - 34) / 2
        probability = html.Div(
            [
                html.Span(
                    f"{TEAM1} {ODDS1:.1f}",
                    style={"color": "tomato", "font-weight": "bold", "text-decoration": "underline"},
                ),
                html.Span(
                    f"Draw {ODDS_DRAW:.1f} ",
                    style={
                        "color": "palegreen",
                        "padding-left": "2vh",
                        "padding-right": "2vh",
                    },
                ),
                html.Span(f"{TEAM2} {ODDS2:.1f}", style={"color": "lightskyblue"}),
            ],
            style={"display": "flex", "justify-content": "center"},
        )
    elif ODDS2 > ODDS_DRAW and ODDS2 > ODDS1:
        probability = html.Div(
            [
                html.Span(f"{TEAM1} {ODDS1:.1f}", style={"color": "tomato"}),
                html.Span(
                    f"Draw {ODDS_DRAW:.1f} ",
                    style={
                        "color": "palegreen",
                        "padding-left": "2vh",
                        "padding-right": "2vh",
                    },
                ),
                html.Span(
                    f"{TEAM2} {ODDS2:.1f}",
                    style={"color": "lightskyblue", "font-weight": "bold", "text-decoration": "underline"},
                ),
            ],
            style={"display": "flex", "justify-content": "center"},
        )
        chance = 67 + (ODDS2 - 34) / 2
    else:
        probability = html.Div(
            [
                html.Span(f"{TEAM1} {ODDS1:.1f}", style={"color": "tomato"}),
                html.Span(
                    f"Draw {ODDS_DRAW:.1f} ",
                    style={
                        "color": "palegreen",
                        "font-weight": "bold",
                        "padding-left": "2vh",
                        "padding-right": "2vh",
                        "font-weight": "bold",
                        "text-decoration": "underline"
                    },
                ),
                html.Span(f"{TEAM2} {ODDS2:.1f}", style={"color": "lightskyblue"}),
            ],
            style={"display": "flex", "justify-content": "center"},
        )
        chance = 50 + (ODDS2 / 3 - ODDS1 / 3) * 1.2

    # probability = html.Div([html.Span(f'{TEAM1} {ODDS1:.1f}', style={'color': 'tomato'}),
    #   html.Span(f'Draw {ODDS_DRAW:.1f} ', style={'color': 'palegreen', 'padding-left': '2vh', 'padding-right': '2vh'}),
    #   html.Span(f'{TEAM2} {ODDS2:.1f}', style={'color': 'lightskyblue', 'font-weight': 'bold'}),
    # ], style={'display': 'flex', 'justify-content': 'center'})

    return (
        fig,
        chance,
        children,
        probability,
    )


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
