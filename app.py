import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd

from youtube_scraper import get_channel_videos

app = dash.Dash(__name__)
server = app.server

# =========================
# STYLES
# =========================
PAGE_STYLE = {
    "backgroundColor": "#f5f7fa",
    "minHeight": "100vh",
    "padding": "40px 30px 30px 30px",  # top padding fixed
    "fontFamily": "Arial, sans-serif"
}

CARD_STYLE = {
    "backgroundColor": "white",
    "borderRadius": "12px",
    "padding": "20px",
    "boxShadow": "0 6px 18px rgba(0,0,0,0.08)",
    "marginBottom": "20px"
}

PRIMARY_BUTTON = {
    "padding": "10px 16px",
    "borderRadius": "6px",
    "border": "none",
    "backgroundColor": "#4f46e5",
    "color": "white",
    "cursor": "pointer",
    "fontWeight": "500"
}

SECONDARY_BUTTON = {
    "padding": "10px 16px",
    "borderRadius": "6px",
    "border": "1px solid #4f46e5",
    "backgroundColor": "white",
    "color": "#4f46e5",
    "cursor": "pointer",
    "fontWeight": "500"
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

TOAST_ANIMATION = {
    "animation": "slideDownFade 0.4s ease-out"
}

# =========================
# LAYOUT
# =========================
app.layout = html.Div(
    style=PAGE_STYLE,
    children=[

        # ---- CSS animation ----
        dcc.Markdown(
            """
<style>
@keyframes slideDownFade {
    from { opacity: 0; transform: translateY(-12px); }
    to   { opacity: 1; transform: translateY(0); }
}
</style>
            """,
            dangerously_allow_html=True
        ),

        # -------- PROJECT HEADER --------
        html.Div(
            children=[
                html.H1(
                    "YouTube Data Visualization Dashboard",
                    style={"marginBottom": "6px", "fontWeight": "700", "color": "#111827"}
                ),
                html.P(
                    "Analyze views, likes, comments, and engagement across YouTube channels",
                    style={"marginTop": "0", "color": "#6b7280", "fontSize": "15px"}
                ),
            ],
            style={"textAlign": "center", "marginBottom": "30px"}
        ),

        # ---- Stores ----
        dcc.Store(id="data-store"),
        dcc.Store(id="toast-store"),

        dcc.Interval(
            id="toast-timer",
            interval=3000,
            n_intervals=0,
            disabled=True
        ),

        # -------- CHANNEL HEADER --------
        html.Div(id="channel-header", style={"textAlign": "center", "marginBottom": "20px"}),

        # -------- CONTROLS --------
        html.Div(
            style={**CARD_STYLE, "marginTop": "10px"},
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
                        html.Button("Load Channel", id="load-button", n_clicks=0, style=PRIMARY_BUTTON),
                        html.Button("Refresh Data", id="refresh-button", n_clicks=0, style=SECONDARY_BUTTON),
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

                        html.Div(
                            style=CARD_STYLE,
                            children=[
                                dcc.Graph(id="bar-chart"),
                                html.P(
                                    "Bars represent the top 10 videos ranked by the selected metric. "
                                    "Hover to see full video titles.",
                                    style={"fontSize": "13px", "color": "#555", "textAlign": "center"}
                                )
                            ]
                        ),

                        html.Div(style=CARD_STYLE, children=[dcc.Graph(id="scatter-chart")]),
                    ]
                )
            ]
        )
    ]
)

# =========================
# LOAD / REFRESH DATA
# =========================
@app.callback(
    Output("data-store", "data"),
    Output("toast-store", "data"),
    Output("channel-header", "children"),
    Input("load-button", "n_clicks"),
    Input("refresh-button", "n_clicks"),
    State("channel-input", "value"),
    prevent_initial_call=True
)
def load_data(load_clicks, refresh_clicks, channel_url):
    if not channel_url:
        return None, {"type": "error", "text": "Please enter a channel URL"}, ""

    refresh = refresh_clicks > load_clicks
    df, channel_name, channel_logo = get_channel_videos(channel_url, refresh=refresh)

    if df.empty:
        return None, {"type": "error", "text": "No data found for this channel"}, ""

    header = html.Div(
        children=[
            html.Img(src=channel_logo, style={"height": "80px", "borderRadius": "50%"}),
            html.H2(channel_name)
        ]
    )

    return df.to_dict("records"), {"type": "success", "text": "Channel loaded successfully"}, header

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

    df["like_rate"] = (df["likes"] / df["views"]) * 100
    df["comment_rate"] = (df["comments"] / df["views"]) * 100
    df = df.replace([float("inf"), -float("inf")], 0).fillna(0)

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

# =========================
# TOAST HANDLER
# =========================
@app.callback(
    Output("toast-message", "children"),
    Output("toast-timer", "disabled"),
    Input("toast-store", "data"),
    Input("toast-timer", "n_intervals")
)
def handle_toast(toast_data, _):
    if not toast_data:
        return "", True

    style = TOAST_SUCCESS if toast_data["type"] == "success" else TOAST_ERROR
    icon = "✅" if toast_data["type"] == "success" else "❌"

    return html.Div(
        [icon, toast_data["text"]],
        style={**style, **TOAST_ANIMATION}
    ), False


if __name__ == "__main__":
    app.run(debug=True)
