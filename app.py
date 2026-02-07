import dash
from dash import dcc, html
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
# Sort videos by views (descending)
df = df.sort_values(by="views", ascending=False)

# Take top 10 videos
df = df.head(10)

# =========================
# VISUALIZATION
# =========================
fig = px.bar(
    df,
    x="title",
    y="views",
    title="Top 10 Most Viewed Videos",
    labels={
        "views": "View Count",
        "title": "Video Title"
    }
)

fig.update_layout(
    xaxis_tickangle=-45,
    height=600,
    margin=dict(b=200)
)

# =========================
# DASH APP
# =========================
app = dash.Dash(__name__)
server = app.server  # needed later for deployment

app.layout = html.Div(
    style={"padding": "20px"},
    children=[
        html.H1("YouTube Data Visualization Dashboard"),
        dcc.Graph(figure=fig)
    ]
)

# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    app.run(debug=True)
