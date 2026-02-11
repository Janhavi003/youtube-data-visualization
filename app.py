import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px

from youtube_scraper import get_channel_videos

app = dash.Dash(__name__)
server = app.server

# =========================
# STYLES
# =========================
PAGE_STYLE = {
    "backgroundColor": "#f5f7fa",
    "minHeight": "100vh",
    "padding": "30px",
    "fontFamily": "Arial, sans-serif"
}

CARD_STYLE = {
    "backgroundColor": "white",
    "borderRadius": "10px",
    "padding": "20px",
    "boxShadow": "0 4px 10px rgba(0,0,0,0.08)",
    "marginBottom": "20px"
}

HEADER_STYLE = {
    "textAlign": "center",
    "marginBottom": "30px"
}

# =========================
# LAYOUT
# =========================
app.layout = html.Div(
    style=PAGE_STYLE,
    children=[

        # -------- HEADER --------
        html.Div(
            style=HEADER_STYLE,
            children=[
                html.H1("YouTube Data Visualization Dashboard"),
                html.P(
                    "Explore video performance and engagement metrics for any YouTube channel",
                    style={"color": "#555"}
                )
            ]
        ),

        # -------- CONTROLS CARD --------
        html.Div(
            style=CARD_STYLE,
            children=[
                html.Div(
                    style={
                        "display": "flex",
                        "gap": "10px",
                        "flexWrap": "wrap",
                        "justifyContent": "center",
                        "marginBottom": "15px"
                    },
                    children=[
                        dcc.Input(
                            id="channel-input",
                            type="text",
                            placeholder="Paste YouTube channel URL",
                            style={
                                "width": "380px",
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
                                "cursor": "pointer"
                            }
                        ),
                        html.Button(
                            "Refresh Data",
                            id="refresh-button",
                            n_clicks=0,
                            style={
                                "padding": "10px 16px",
                                "borderRadius": "6px",
                                "border": "1px solid #4f46e5",
                                "backgroundColor": "white",
                                "color": "#4f46e5",
                                "cursor": "pointer"
                            }
                        ),
                    ]
                ),

                html.Div(
                    style={"maxWidth": "300px", "margin": "0 auto"},
                    children=[
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
                            clearable=False
                        )
                    ]
                )
            ]
        ),

        # -------- CHARTS --------
        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gap": "20px"
            },
            children=[
                html.Div(style=CARD_STYLE, children=[
                    dcc.Graph(id="bar-chart")
                ]),
                html.Div(style=CARD_STYLE, children=[
                    dcc.Graph(id="scatter-chart")
                ]),
            ]
        )
    ]
)

# =========================
# CALLBACK
# =========================
@app.callback(
    Output("bar-chart", "figure"),
    Output("scatter-chart", "figure"),
    Input("load-button", "n_clicks"),
    Input("refresh-button", "n_clicks"),
    State("channel-input", "value"),
    State("metric-dropdown", "value")
)
def update_charts(load_clicks, refresh_clicks, channel_url, metric):
    if not channel_url:
        empty = px.scatter(title="Enter a YouTube channel URL and click Load")
        return empty, empty

    refresh = refresh_clicks > load_clicks
    df = get_channel_videos(channel_url, refresh=refresh)

    if df.empty:
        empty = px.scatter(title="No data found for this channel")
        return empty, empty

    df["like_rate"] = (df["likes"] / df["views"]) * 100
    df["comment_rate"] = (df["comments"] / df["views"]) * 100
    df = df.replace([float("inf"), -float("inf")], 0).fillna(0)

    df_bar = df.sort_values(by=metric, ascending=False).head(10)

    bar_fig = px.bar(
        df_bar,
        x="title",
        y=metric,
        title=f"Top 10 Videos by {metric.replace('_', ' ').title()}"
    )
    bar_fig.update_layout(xaxis_tickangle=-45, margin=dict(b=200))

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
    app.run(debug=True)
