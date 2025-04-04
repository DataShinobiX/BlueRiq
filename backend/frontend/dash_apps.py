# frontend/dash_apps.py

from django_plotly_dash import DjangoDash
import dash_core_components as dcc
import dash_html_components as html

app = DjangoDash("MyDashApp")  # 👈 this must match template

app.layout = html.Div([
    html.H2("Hello from Dash!"),
    dcc.Graph(figure={
        'data': [{'x': [1, 2, 3], 'y': [3, 1, 2], 'type': 'bar'}],
        'layout': {'title': 'Sample Chart'}
    })
])
