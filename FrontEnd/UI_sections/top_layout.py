import dash
from dash import dcc, html

def get_top_layout():
    
    top_layout = [
            # Tabs section
            html.Div(
                className="files-container",
                children=[
                    html.Button(
                        className="files-button",
                        id="files_button",
                        children="Files",
                    ),
                ]
            ),

            # App Title
            html.Div(
                className="title-container",
                children=[
                    html.H2(
                        className="title",
                        children="Ostinato Live",
                    )
                ]
            ),

            # Class; members
            html.Div(
                className="members-container",
                children=[
                    html.H5(
                        "CS 467 | Winter 2025 ©",
                        style={"padding": "2px",
                               "margin": "0px"}
                    ),
                    html.H5(
                        "Arthur Tripp | Quyen Nguyen | Matthew Pennington",
                        style={"padding": "0px",
                               "margin": "0px"}
                    ),
                ]
            )
        ]
    
    return top_layout
