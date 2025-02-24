import os
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import callbacks

from assets.layout import Layout
tempo = 120
beats = 5
layout = Layout(tempo, beats)

# Initialize Dash app
# Note: external stylesheet is for moal/file popup styling
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP])

# Contains the UI layout
app_layout = html.Div(
    className="app-container",
    children=[

        # Links css style file
        html.Link(rel="stylesheet", href=os.path.join("assets", "main_style.css")),
        html.Link(rel="stylesheet", href=os.path.join("assets", "top_style.css")),
        html.Link(rel="stylesheet", href=os.path.join("assets", "bottom_right_style.css")),
        html.Link(rel="stylesheet", href=os.path.join("assets", "bottom_left_style.css")),
        # Link font awesome file to use icons
        html.Link(
            rel="stylesheet",
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css",
        ),
        
        # Top section
        html.Div(
            className="top-container",
            children=layout.get_top_layout()
        ),


        # Bottom section
        html.Div(
            className="bottom-container",
            children=[
                # Left section
                html.Div(
                    className="left-container",
                    children=[

                        # Loop period
                        # Contains loop text, pitch button
                        html.Div(
                            className="loop-container",
                            children=layout.get_loop_layout()
                        ),

                        # Get track layout
                        html.Div(
                            className="track-container",
                            children=[
                                html.Div(
                                    id="track_section",
                                    ),
                                html.Div(
                                    id='playhead',
                                ),
                                dcc.Interval(
                                    id='playhead-interval',
                                    interval=(6000 / callbacks.loop_machine.bpm),
                                    n_intervals=0
                                )
                            ]
                        )
                    ]
                ),

                # Bottom right section
                html.Div(
                    className="right-container",
                    children=layout.get_right_tab_layout()
                ),
            ]
        )
    ]
)


# Add layout to app
app.layout = app_layout

# Get all callbacks
callbacks.button_callbacks(app)
callbacks.playhead_callback(app)

if __name__ == "__main__":
    app.run(debug=True)
