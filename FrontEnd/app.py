import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

import callbacks

# Initialize Dash app
app = dash.Dash(__name__)

# Contains the UI layout
layout = html.Div(
    style = {"display": "flex", "flexDirection": "column"},
    children = [
        
        
        # Links css style file
        html.Link(rel="stylesheet", href="./assets/main_style.css"),
        
        
        # Top section
        html.Div(
            className="top-container",
            children=[
                
                # Tabs section
                html.Div(
                    className="tabs-container",
                    children=[
                        ]
                    ),
                
                # App Title
                html.Div(
                    className="app-container",
                    children=[
                        html.H4(
                            "Audio Loop Station",
                            className="title"
                            )
                        ]
                    ),
                
                # Class; members
                html.Div(
                    className="members-container",
                    children=[
                        ]
                    )
                ]
            ),
        
        
        # Right section
        html.Div(
            className="right-container"
            ),
        
        
        # Left section
        html.Div(
            className="left-container"
            ),
        
        ]
    )

# Add layout to app
app.layout = layout

if __name__ == "__main__":
    app.run(debug=True)