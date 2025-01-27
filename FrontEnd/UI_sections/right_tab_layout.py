import dash
from dash import dcc, html


def get_right_tab_layout():

    right_layout = [
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

    return right_layout
