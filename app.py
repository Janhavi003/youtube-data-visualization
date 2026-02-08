import dash
from dash import dcc, html, Input, Output
import plotly.express as px

from youtube_scraper import get_channel_videos

# =========================
# CONFIG
# =========================
CHANNEL_URL = "https://www.youtube.com/@GoogleDevelopers/videos"

# =========================
# DATA FETCHING
# =========================
df = get_channel_videos(CHANNEL_URL)

# =========================
# DATA TRANSFORMATION
# =========================
df = df.sort_values(by="views", ascending=False)
df = df.head(10)

# =========================
# DASH APP
# =========================
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    style={"padding": "20px"},
    children=[
        html.H1("YouTube Data Visualization Dashboard"),

        # -------- DROPDOWN --------
        dcc.Dropdown(
            id="metric-dropdown",
            options=[
                {"label": "Views", "value": "views"},
                {"label": "Likes", "value": "likes"},
                {"label": "Comments", "value": "comments"},
            ],
            value="views",
            clearable=False,
            style={"width": "300px"}
        ),

        dcc.Graph(id="bar-chart")
    ]
)

# =========================
# CALLBACK
# =========================
@app.callback(
    Output("bar-chart", "figure"),
    Input("metric-dropdown", "value")
)
def update_chart(selected_metric):
    fig = px.bar(
        df,
        x="title",
        y=selected_metric,
        title=f"Top 10 Videos by {selected_metric.capitalize()}",
        labels={
            selected_metric: selected_metric.capitalize(),
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
