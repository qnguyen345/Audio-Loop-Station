import dash
from dash import dcc, html


def get_loop_layout():

    loop_layout = [
            html.Div(
                className="left-loop-tab-section-container",
                children=[

                    # Loop text
                    html.Span(
                        className="loop-period-text",
                        children="Loop Period"
                    ),

                    html.Div(
                        className="left-loop-row-container",
                        children=[
                            # Pitch button
                            html.Button(
                                className="pitch-button",
                                id="pitch_button_0",
                                children="Pitch"
                            ),

                            # Trash button
                            html.Button(
                                className="trash-button",
                                id="trash_button_0",
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

    return loop_layout
