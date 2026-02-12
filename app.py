import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd

from youtube_scraper import get_channel_videos

app = dash.Dash(__name__)
server = app.server   # REQUIRED for gunicorn


# =========================
# LAYOUT
# =========================
app.layout = html.Div(
    style={
        "backgroundColor": "#f5f7fa",
        "minHeight": "100vh",
        "padding": "40px 30px",
        "fontFamily": "Arial, sans-serif"
    },
    children=[

        # -------- TITLE --------
        html.Div(
            style={"textAlign": "center", "marginBottom": "30px"},
            children=[
                html.H1("YouTube Data Visualization Dashboard"),
                html.P(
                    "Analyze views, likes, comments, and engagement across YouTube channels",
                    style={"color": "#6b7280"}
                )
            ]
        ),

        dcc.Store(id="data-store"),

        # -------- CONTROLS --------
        html.Div(
            style={
                "background": "white",
                "borderRadius": "12px",
                "padding": "20px",
                "boxShadow": "0 6px 18px rgba(0,0,0,0.08)",
                "marginBottom": "20px"
            },
            children=[
                html.Div(
                    style={
                        "display": "flex",
                        "gap": "12px",
                        "justifyContent": "center",
                        "flexWrap": "wrap",
                        "marginBottom": "18px"
                    },
                    children=[
                        dcc.Input(
                            id="channel-input",
                            type="text",
                            placeholder="Paste YouTube channel URL",
                            style={
                                "width": "420px",
                                "padding": "10px",
                                "borderRadius": "6px",
                                "border": "1px solid #ccc"
                            }
                        ),
                        html.Button(
                            "Load Channel",
                            id="load-button",
                            n_clicks=0,
                            style={
                                "padding": "10px 16px",
                                "borderRadius": "6px",
                                "border": "none",
                                "backgroundColor": "#4f46e5",
                                "color": "white",
                                "cursor": "pointer",
                                "fontWeight": "500"
                            }
                        ),
                    ]
                ),

                dcc.Dropdown(
                    id="metric-dropdown",
                    options=[
                        {"label": "Views", "value": "views"},
                        {"label": "Likes", "value": "likes"},
                        {"label": "Comments", "value": "comments"},
                        {"label": "Like Rate (%)", "value": "like_rate"},
                        {"label": "Comment Rate (%)", "value": "comment_rate"},
                    ],
                    value="views",
                    clearable=False,
                    style={"maxWidth": "300px", "margin": "0 auto"}
                )
            ]
        ),

        # -------- CHARTS --------
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"},
            children=[
                html.Div(
                    style={
                        "background": "white",
                        "borderRadius": "12px",
                        "padding": "20px",
                        "boxShadow": "0 6px 18px rgba(0,0,0,0.08)"
                    },
                    children=[dcc.Graph(id="bar-chart")]
                ),
                html.Div(
                    style={
                        "background": "white",
                        "borderRadius": "12px",
                        "padding": "20px",
                        "boxShadow": "0 6px 18px rgba(0,0,0,0.08)"
                    },
                    children=[dcc.Graph(id="scatter-chart")]
                ),
            ]
        )
    ]
)

# =========================
# LOAD DATA
# =========================
@app.callback(
    Output("data-store", "data"),
    Input("load-button", "n_clicks"),
    State("channel-input", "value"),
    prevent_initial_call=True
)
def load_data(_, channel_url):
    if not channel_url:
        return None

    df, _, _ = get_channel_videos(channel_url)

    if df.empty:
        return None

    return df.to_dict("records")


# =========================
# UPDATE CHARTS
# =========================
@app.callback(
    Output("bar-chart", "figure"),
    Output("scatter-chart", "figure"),
    Input("metric-dropdown", "value"),
    Input("data-store", "data")
)
def update_charts(metric, data):
    if not data:
        return px.scatter(), px.scatter()

    df = pd.DataFrame(data)

    # Safe metrics
    df["like_rate"] = (df["likes"] / df["views"]).replace([float("inf")], 0) * 100
    df["comment_rate"] = (df["comments"] / df["views"]).replace([float("inf")], 0) * 100
    df = df.fillna(0)

    df_bar = df.sort_values(by=metric, ascending=False).head(10).reset_index(drop=True)
    df_bar["rank"] = df_bar.index + 1

    bar_fig = px.bar(
        df_bar,
        x="rank",
        y=metric,
        hover_data={"title": True},
        title=f"Top 10 Videos by {metric.replace('_', ' ').title()}"
    )

    scatter_fig = px.scatter(
        df,
        x="views",
        y="like_rate",
        size="likes",
        hover_name="title",
        title="Views vs Like Rate"
    )

    return bar_fig, scatter_fig


if __name__ == "__main__":
    app.run()
