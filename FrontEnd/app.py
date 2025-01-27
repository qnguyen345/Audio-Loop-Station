import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import callbacks

import UI_sections.tracks_layout as tracks_layout
import UI_sections.right_tab_layout as right_tab_layout
import UI_sections.top_layout as top_layout
import UI_sections.loop_layout as loop_layout

# Initialize Dash app
# Note: external stylesheet is for moal/file popup styling
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Contains the UI layout
layout = html.Div(
    className="app-container",
    children=[

        # Links css style file
        html.Link(rel="stylesheet", href="./assets/main_style.css"),
        html.Link(rel="stylesheet", href="./assets/top_style.css"),
        html.Link(rel="stylesheet", href="./assets/bottom_right_style.css"),
        html.Link(rel="stylesheet", href="./assets/bottom_left_style.css"),
        # Link font awesome file to use icons
        html.Link(
            rel="stylesheet",
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css",
        ),


        # Store components to keep track of the number of track sections
        dcc.Store(id="track_index", data={"index": 6}),

        # Top section
        html.Div(
            className="top-container",
            children=top_layout.get_top_layout()
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
                            children=loop_layout.get_loop_layout()
                        ),

                        # Get track layout
                        html.Div(
                            className="track-container",
                            children=tracks_layout.get_track_layout()
                        )

                    ]
                ),

                # Bottom right section
                html.Div(
                    className="right-container",
                    children=right_tab_layout.get_right_tab_layout()
                ),
            ]
        )
    ]
)


# Add layout to app
app.layout = layout

# Get all callbacks
callbacks.button_callbacks(app)
callbacks.add_new_track_section(app)

if __name__ == "__main__":
    app.run(debug=True)
