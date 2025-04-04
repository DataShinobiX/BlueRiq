# frontend/dash_apps.py
from django_plotly_dash import DjangoDash
from dash import html, dcc

app = DjangoDash("HighlightingProgram")

app.layout = html.Div(
    style={'textAlign': 'center', 'marginTop': '50px'},
    children=[
        # Title
        html.H1("AUTOMATIC HIGHLIGHTING PROGRAM"),

        # Row with Upload and Dropdown
        html.Div(
            style={'display': 'flex', 'justifyContent': 'center', 'gap': '40px', 'margin': '40px'},
            children=[
                # Upload button
                dcc.Upload(
                    id='upload-pdf',
                    children=html.Button("UPLOAD", id='upload-button'),
                    multiple=False,  # Only 1 PDF
                    style={
                        'border': '2px dashed #ccc',
                        'padding': '20px',
                        'cursor': 'pointer'
                    }
                ),

                # Dropdown
                dcc.Dropdown(
                    id='my-dropdown',
                    options=[
                        {'label': 'Option 1', 'value': 'opt1'},
                        {'label': 'Option 2', 'value': 'opt2'},
                        {'label': 'Option 3', 'value': 'opt3'},
                    ],
                    placeholder="Select an option",
                    style={'width': '200px'}
                ),
            ]
        ),

        # Submit button (centered)
        html.Button("SUBMIT", id='submit-button', style={'padding': '10px 20px'}),
    ]
)
