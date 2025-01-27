import dash
from dash import dcc, html

def get_track_layout():
    track_layout = [
            # Track container (#1)
            html.Div(
                className="track-tabs-container",
                children=[
                    html.Div(
                        className="left-tab-section-container",
                        children=[
                            html.Span(className="track-text", children="Track 1"),
                            html.Div(
                                className="left-row-container",
                                children=[
                                    # Play icon button
                                    html.Button(
                                        className="left-play-icon-button",
                                        id="left_play_icon_button_1",
                                        children=[html.I(className="fa-solid fa-play")],
                                    ),
                                    # Mute/unmute icon button
                                    html.Button(
                                        className="left-mute-icon-button",
                                        id="left_mute_icon_button_1",
                                        children=[html.I(className="fa-solid fa-volume-xmark")],
                                    ),
                                    # Trash button
                                    html.Button(
                                        className="trash-button",
                                        id="trash_button_1",
                                        children=[html.I(className="fa-solid fa-trash")],
                                    ),
                                ],
                            ),
                            # Pitch button
                            html.Button(
                                className="pitch-button",
                                id="pitch_button_1",
                                children="Pitch",
                            ),
                        ],
                    ),
                ],
            ),
            # Track container (#2)
            html.Div(
                className="track-tabs-container",
                children=[
                    html.Div(
                        className="left-tab-section-container",
                        children=[
                            html.Span(className="track-text", children="Track 2"),
                            html.Div(
                                className="left-row-container",
                                children=[
                                    # Play icon button
                                    html.Button(
                                        className="left-play-icon-button",
                                        id="left_play_icon_button_2",
                                        children=[html.I(className="fa-solid fa-play")],
                                    ),
                                    # Mute/unmute icon button
                                    html.Button(
                                        className="left-mute-icon-button",
                                        id="left_mute_icon_button_2",
                                        children=[html.I(className="fa-solid fa-volume-xmark")],
                                    ),
                                    # Trash button
                                    html.Button(
                                        className="trash-button",
                                        id="trash_button_2",
                                        children=[html.I(className="fa-solid fa-trash")],
                                    ),
                                ],
                            ),
                            # Pitch button
                            html.Button(
                                className="pitch-button",
                                id="pitch_button_2",
                                children="Pitch",
                            ),
                        ],
                    ),
                ],
            ),
            # Track container (#3)
            html.Div(
                className="track-tabs-container",
                children=[
                    html.Div(
                        className="left-tab-section-container",
                        children=[
                            html.Span(className="track-text", children="Track 3"),
                            html.Div(
                                className="left-row-container",
                                children=[
                                    # Play icon button
                                    html.Button(
                                        className="left-play-icon-button",
                                        id="left_play_icon_button_3",
                                        children=[html.I(className="fa-solid fa-play")],
                                    ),
                                    # Mute/unmute icon button
                                    html.Button(
                                        className="left-mute-icon-button",
                                        id="left_mute_icon_button_3",
                                        children=[html.I(className="fa-solid fa-volume-xmark")],
                                    ),
                                    # Trash button
                                    html.Button(
                                        className="trash-button",
                                        id="trash_button_3",
                                        children=[html.I(className="fa-solid fa-trash")],
                                    ),
                                ],
                            ),
                            # Pitch button
                            html.Button(
                                className="pitch-button",
                                id="pitch_button_3",
                                children="Pitch",
                            ),
                        ],
                    ),
                ],
            ),
            # Track container (#4)
            html.Div(
                className="track-tabs-container",
                children=[
                    html.Div(
                        className="left-tab-section-container",
                        children=[
                            html.Span(className="track-text", children="Track 4"),
                            html.Div(
                                className="left-row-container",
                                children=[
                                    # Play icon button
                                    html.Button(
                                        className="left-play-icon-button",
                                        id="left_play_icon_button_4",
                                        children=[html.I(className="fa-solid fa-play")],
                                    ),
                                    # Mute/unmute icon button
                                    html.Button(
                                        className="left-mute-icon-button",
                                        id="left_mute_icon_button_4",
                                        children=[html.I(className="fa-solid fa-volume-xmark")],
                                    ),
                                    # Trash button
                                    html.Button(
                                        className="trash-button",
                                        id="trash_button_4",
                                        children=[html.I(className="fa-solid fa-trash")],
                                    ),
                                ],
                            ),
                            # Pitch button
                            html.Button(
                                className="pitch-button",
                                id="pitch_button_4",
                                children="Pitch",
                            ),
                        ],
                    ),
                ],
            ),
            # Track container (#5)
            html.Div(
                className="track-tabs-container",
                children=[
                    html.Div(
                        className="left-tab-section-container",
                        children=[
                            html.Span(className="track-text", children="Track 5"),
                            html.Div(
                                className="left-row-container",
                                children=[
                                    # Play icon button
                                    html.Button(
                                        className="left-play-icon-button",
                                        id="left_play_icon_button_5",
                                        children=[html.I(className="fa-solid fa-play")],
                                    ),
                                    # Mute/unmute icon button
                                    html.Button(
                                        className="left-mute-icon-button",
                                        id="left_mute_icon_button_5",
                                        children=[html.I(className="fa-solid fa-volume-xmark")],
                                    ),
                                    # Trash button
                                    html.Button(
                                        className="trash-button",
                                        id="trash_button_5",
                                        children=[html.I(className="fa-solid fa-trash")],
                                    ),
                                ],
                            ),
                            # Pitch button
                            html.Button(
                                className="pitch-button",
                                id="pitch_button_5",
                                children="Pitch",
                            ),
                        ],
                    ),
                ],
            ),
            # Track container (#6)
            html.Div(
                className="track-tabs-container",
                children=[
                    html.Div(
                        className="left-tab-section-container",
                        children=[
                            html.Span(className="track-text", children="Track 6"),
                            html.Div(
                                className="left-row-container",
                                children=[
                                    # Play icon button
                                    html.Button(
                                        className="left-play-icon-button",
                                        id="left_play_icon_button_6",
                                        children=[html.I(className="fa-solid fa-play")],
                                    ),
                                    # Mute/unmute icon button
                                    html.Button(
                                        className="left-mute-icon-button",
                                        id="left_mute_icon_button_6",
                                        children=[html.I(className="fa-solid fa-volume-xmark")],
                                    ),
                                    # Trash button
                                    html.Button(
                                        className="trash-button",
                                        id="trash_button_6",
                                        children=[html.I(className="fa-solid fa-trash")],
                                    ),
                                ],
                            ),
                            # Pitch button
                            html.Button(
                                className="pitch-button",
                                id="pitch_button_6",
                                children="Pitch",
                            ),
                        ],
                    ),
                ],
            ),
        ]
    
    return track_layout
    
