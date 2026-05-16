import os
from dash import Dash, html
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

app.layout = html.Div([
    html.H3("DPE Sport Pilot Oral Examiner",
            style={"color": "#58A6FF", "fontFamily": "monospace", "padding": "40px"})
])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=False, port=port)
