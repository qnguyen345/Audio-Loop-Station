import os
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import callbacks

from assets.layout import Layout

# Initialize Dash app
# Note: external stylesheet is for moal/file popup styling
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP])

# Inital tempo and duration
tempo = 5000
duration = 120

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

        # Store duration and tempo
        dcc.Store(id="stored_duration", data=duration),
        dcc.Store(id="stored_tempo", data=tempo),
        
        # Initialize and store track list
        dcc.Store(id="stored_track_list", data=["Dummy_1"]), #Initialize to 'Dummy'
        
        # Top section
        html.Div(
            className="top-container",
            children=Layout.get_top_layout()
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
                            children=Layout.get_loop_layout()
                        ),

                        # Get track layout
                        html.Div(
                            className="track-container",
                            children=[
                                Layout.get_add_track_layout(),
                                html.Div(
                                    id="track_section",
                                    )
                                ]
                        )

                    ]
                ),

                # Bottom right section
                html.Div(
                    className="right-container",
                    children=Layout(tempo, duration).get_right_tab_layout()
                ),
            ]
        )
    ]
)


# Add layout to app
app.layout = app_layout

# Get all callbacks
callbacks.button_callbacks(app)
callbacks.update_layout_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)
