import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

import callbacks

# Initialize Dash app
app = dash.Dash(__name__)

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


        # Top section
        html.Div(
            className="top-container",
            children=[

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
                        html.Div(
                            className="loop-container",
                            children=[

                                # Contains loop text, pitch button
                                html.Div(
                                    className="left-tab-section-container",
                                    children=[

                                        # Loop text
                                        html.Span(
                                            className="loop-period-text",
                                            children="Loop Period"
                                        ),

                                        html.Div(
                                            className="left-row-container",
                                            children=[
                                                # Pitch button
                                                html.Button(
                                                    className="pitch-button",
                                                    id="pitch_button",
                                                    children="Pitch"
                                                ),

                                                # Trash button
                                                html.Button(
                                                    className="trash-button",
                                                    id="trash_button",
                                                    children=[
                                                        html.I(
                                                            className="fa-solid fa-trash"
                                                        )
                                                    ]
                                                )
                                            ]
                                        )
                                    ]
                                ),  
                            ]
                        ),
                        
                        # Track container (#1)
                        html.Div(
                            className="track-container",
                            children=[

                                # Contains loop text, pitch button
                                html.Div(
                                    className="left-tab-section-container",
                                    children=[

                                        # Loop text
                                        html.Span(
                                            className="track-text",
                                            children="Track 1"
                                        ),

                                        html.Div(
                                            className="left-row-container",
                                            children=[
                                                # Play icon button
                                                html.Button(
                                                    className="left-play-icon-button",
                                                    id="left_play_icon_button",
                                                    children=[
                                                        html.I(className="fa-solid fa-play"),
                                                        ]
                                                ),
                                                
                                                # Mute/unmute icon button
                                                html.Button(
                                                    className="left-mute-icon-button",
                                                    id="left_mute_icon_button",
                                                    children=[
                                                        html.I(className="fa-solid fa-volume-xmark"),
                                                        ]
                                                ),

                                                # Trash button
                                                html.Button(
                                                    className="trash-button",
                                                    id="trash_button",
                                                    children=[
                                                        html.I(
                                                            className="fa-solid fa-trash"
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                        
                                        # Pitch button
                                        html.Button(
                                            className="pitch-button",
                                            id="pitch_button",
                                            children="Pitch"
                                        ),
                                        
                                    ]
                                ),  
                            ]
                        ),
                        
                        
                    ]
                ),

                # Bottom right section
                html.Div(
                    className="right-container",
                    children=[

                        # First row of right section
                        # Contains record, pause and stop buttons
                        html.Div(
                            className="right-first-second-row-container",
                            children=[

                                # Record Button and text
                                html.Button(
                                    className="record-button",
                                    id="record_button",
                                    children=[
                                        html.I(
                                            className="fa-solid fa-microphone"),
                                        html.Span(children="Record",
                                                  className="record-text")
                                    ]
                                ),

                                # Play Button and Text
                                html.Button(
                                    className="play-button",
                                    id="play_button",
                                    children=[
                                        html.I(className="fa-solid fa-play"),
                                        html.Span(children="Play",
                                                  className="play-text")
                                    ]
                                ),

                                # Pause Button and Text
                                html.Button(
                                    className="pause-button",
                                    id="pause_button",
                                    children=[
                                        html.I(className="fa-solid fa-pause"),
                                        html.Span(className="pause-text",
                                                  children="Pause")
                                    ]
                                ),

                                # Stop Button and Text
                                html.Button(
                                    className="stop-button",
                                    id="stop_button",
                                    children=[
                                        html.I(className="fa-solid fa-stop"),
                                        html.Span(children="Stop",
                                                  className="stop-text")
                                    ]
                                ),

                            ]
                        ),

                        # Second row of right section
                        # Contains tempo selection, requirement buttons and
                        # save button
                        html.Div(
                            className="right-third-row-container",
                            children=[

                                # Tempo selection with - + settings
                                html.Div(
                                    className="tempo-container",
                                    id="tempo_container",
                                    children=[
                                        html.Div(
                                            children=[
                                                html.Span(className="tempo-text",
                                                          children="Tempo"),
                                            ]
                                        ),

                                        html.Div(
                                            children=[
                                                html.Button(
                                                    className="tempo-button",
                                                    id="tempo-",
                                                    children="-"
                                                ),
                                                dcc.Input(
                                                    className="tempo-input",
                                                    id="tempo_input",
                                                    type="number",
                                                    value=100, step=None
                                                ),
                                                html.Button(
                                                    className="tempo-button",
                                                    id="tempo+",
                                                    children="+"
                                                ),
                                            ]
                                        )
                                    ]
                                ),
                            ]
                        ),

                        # 3 Requirements Buttons
                        html.Div(
                            className="right-fourth-row-container",
                            children=[

                                # Auto-trimming button
                                html.Button(
                                    className="auto-trim-button",
                                    id="auto_trim_button",
                                    children="Auto-Trim"
                                ),

                                # TO BE WORKED ON
                                html.Button(
                                    className="auto-trim-button",
                                    children="Req.2 Button"
                                ),
                                html.Button(
                                    className="auto-trim-button",
                                    children="Req.3 Button"
                                )
                            ]
                        ),


                        html.Div(
                            className="right-fifth-row-container",
                            children=[
                                
                                 # Save button to save loop
                                 html.Button(
                                     className="delete-loop-button",
                                     id="delete_loop_button",
                                     children=[
                                         html.Span(className="delete-loop-text",
                                                   children="Delete Loop"
                                                   )
                                     ]
                                 ),
                                 
                                # Save button to save loop
                                html.Button(
                                    className="save-button",
                                    id="save_button",
                                    children=[
                                        html.Span(className="save-text",
                                                  children="Save Loop"
                                                  )
                                    ]
                                ),

                            ]
                        ),
                    ]
                ),
            ]
        )
    ]
)


# Add layout to app
app.layout = layout

# Get callbacks
callbacks.button_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)
