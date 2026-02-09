import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd

from youtube_scraper import get_channel_videos

# =========================
# DASH APP
# =========================
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    style={"padding": "20px"},
    children=[
        html.H1("YouTube Data Visualization Dashboard"),

        # -------- CHANNEL INPUT --------
        html.Div(
            style={"marginBottom": "15px"},
            children=[
                dcc.Input(
                    id="channel-input",
                    type="text",
                    placeholder="Paste YouTube channel URL here",
                    style={"width": "400px", "marginRight": "10px"}
                ),
                html.Button("Load Channel", id="load-button", n_clicks=0)
            ]
        ),

        # -------- METRIC DROPDOWN --------
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
            style={"width": "300px", "marginBottom": "20px"}
        ),

        dcc.Graph(id="bar-chart")
    ]
)

# =========================
# CALLBACK
# =========================
@app.callback(
    Output("bar-chart", "figure"),
    Input("load-button", "n_clicks"),
    State("channel-input", "value"),
    State("metric-dropdown", "value")
)
def update_chart(n_clicks, channel_url, metric):
    if not channel_url:
        return px.bar(title="Enter a YouTube channel URL and click Load")

    df = get_channel_videos(channel_url)

    if df.empty:
        return px.bar(title="No data found for this channel")

    # -------- ENGAGEMENT METRICS --------
    df["like_rate"] = (df["likes"] / df["views"]) * 100
    df["comment_rate"] = (df["comments"] / df["views"]) * 100

    # Handle division by zero
    df = df.replace([float("inf"), -float("inf")], 0).fillna(0)

    # Sort + top 10
    df = df.sort_values(by=metric, ascending=False).head(10)

    fig = px.bar(
        df,
        x="title",
        y=metric,
        title=f"Top 10 Videos by {metric.replace('_', ' ').title()}",
        labels={
            metric: metric.replace("_", " ").title(),
            "title": "Video Title"
        }
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        height=600,
        margin=dict(b=200)
    )

    return fig

# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    app.run(debug=True)
