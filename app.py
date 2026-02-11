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
    "borderRadius": "12px",
    "padding": "20px",
    "boxShadow": "0 6px 18px rgba(0,0,0,0.08)",
    "marginBottom": "20px"
}

TOAST_SUCCESS = {
    "display": "inline-flex",
    "alignItems": "center",
    "gap": "8px",
    "backgroundColor": "#e6fffa",
    "color": "#065f46",
    "padding": "10px 16px",
    "borderRadius": "8px",
    "border": "1px solid #99f6e4",
    "fontWeight": "500",
    "margin": "10px auto",
    "maxWidth": "fit-content"
}

TOAST_ERROR = {
    "display": "inline-flex",
    "alignItems": "center",
    "gap": "8px",
    "backgroundColor": "#fee2e2",
    "color": "#7f1d1d",
    "padding": "10px 16px",
    "borderRadius": "8px",
    "border": "1px solid #fecaca",
    "fontWeight": "500",
    "margin": "10px auto",
    "maxWidth": "fit-content"
}

# =========================
# LAYOUT
# =========================
app.layout = html.Div(
    style=PAGE_STYLE,
    children=[

        # -------- CHANNEL HEADER --------
        html.Div(id="channel-header", style={"textAlign": "center", "marginBottom": "20px"}),

        # -------- CONTROLS --------
        html.Div(
            style=CARD_STYLE,
            children=[
                html.Div(
                    style={
                        "display": "flex",
                        "gap": "10px",
                        "justifyContent": "center",
                        "flexWrap": "wrap",
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
                        html.Button("Load Channel", id="load-button", n_clicks=0),
                        html.Button("Refresh Data", id="refresh-button", n_clicks=0),
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

        # -------- TOAST --------
        html.Div(id="toast-message", style={"textAlign": "center"}),

        # -------- CHARTS --------
        dcc.Loading(
            type="circle",
            children=[
                html.Div(
                    style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"},
                    children=[

                        # ---- BAR CHART CARD ----
                        html.Div(
                            style=CARD_STYLE,
                            children=[
                                dcc.Graph(id="bar-chart"),
                                html.P(
                                    "Bars represent the top 10 videos ranked by the selected metric. "
                                    "Hover on bars to see full video titles.",
                                    style={
                                        "fontSize": "13px",
                                        "color": "#555",
                                        "marginTop": "10px",
                                        "textAlign": "center"
                                    }
                                )
                            ]
                        ),

                        # ---- SCATTER CARD ----
                        html.Div(style=CARD_STYLE, children=[dcc.Graph(id="scatter-chart")]),
                    ]
                )
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
    Output("toast-message", "children"),
    Output("channel-header", "children"),
    Input("load-button", "n_clicks"),
    Input("refresh-button", "n_clicks"),
    State("channel-input", "value"),
    State("metric-dropdown", "value")
)
def update_dashboard(load_clicks, refresh_clicks, channel_url, metric):
    if not channel_url:
        return px.scatter(), px.scatter(), "", ""

    refresh = refresh_clicks > load_clicks
    df, channel_name, channel_logo = get_channel_videos(channel_url, refresh=refresh)

    if df.empty:
        toast = html.Div(["❌", "No data found for this channel"], style=TOAST_ERROR)
        return px.scatter(), px.scatter(), toast, ""

    # -------- METRICS --------
    df["like_rate"] = (df["likes"] / df["views"]) * 100
    df["comment_rate"] = (df["comments"] / df["views"]) * 100
    df = df.replace([float("inf"), -float("inf")], 0).fillna(0)

    # Sort & rank
    df_bar = df.sort_values(by=metric, ascending=False).head(10).reset_index(drop=True)
    df_bar["rank"] = df_bar.index + 1

    # -------- BAR CHART (NO TITLES) --------
    bar_fig = px.bar(
        df_bar,
        x="rank",
        y=metric,
        hover_data={"title": True},
        labels={
            "rank": "Rank",
            metric: metric.replace("_", " ").title()
        },
        title=f"Top 10 Videos by {metric.replace('_', ' ').title()}"
    )

    bar_fig.update_layout(
        xaxis=dict(tickmode="linear"),
        height=500
    )

    # -------- SCATTER --------
    scatter_fig = px.scatter(
        df,
        x="views",
        y="like_rate",
        size="likes",
        hover_name="title",
        title="Views vs Like Rate",
        labels={"views": "Views", "like_rate": "Like Rate (%)"}
    )

    # -------- HEADER --------
    header = html.Div(
        children=[
            html.Img(
                src=channel_logo,
                style={"height": "80px", "borderRadius": "50%", "marginBottom": "8px"}
            ),
            html.H2(channel_name)
        ]
    )

    toast = html.Div(["✅", "Channel loaded successfully"], style=TOAST_SUCCESS)

    return bar_fig, scatter_fig, toast, header


if __name__ == "__main__":
    app.run(debug=True)
