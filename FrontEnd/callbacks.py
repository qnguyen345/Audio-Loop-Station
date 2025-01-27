import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State


def button_callbacks(app):
    """Callbacks for button animations and interactions."""

    @app.callback(
        Output("record_button", "className"),
        Input("record_button", "n_clicks"),
        prevent_initial_call=True
    )
    def record_pulse(n_clicks):
        """
        Makes the record buttons pulsing red to indicate recording.
        Parameters:
        -----------
            n-clicks (int or None): number of button clicks. Initially None.
        Returns:
        -------
            button className: contains the button className for css styling
        """
        if n_clicks is None or n_clicks % 2 == 0:
            return "record-button"
        # Pulsing for clicked button
        else:
            return "record-button-pulsing pulse"

    @app.callback(
        Output("tempo_input", "value"),
        [Input("tempo-", "n_clicks"),
         Input("tempo+", "n_clicks"),
         Input("tempo_input", "value")],
        prevent_initial_call=True
    )
    def set_tempo(decrease_tempo, increase_tempo, set_tempo):
        """
        Sets the tempo if a user adds an input or if the user uses the "-" or
        "+" button to decrease or increase the tempo.
        Parameters:
        -----------
            decrease_tempo (int or None): number of "-" button clicks.
                Initially None.
            increase_tempo (int or None): number of "+" button clicks.
                Initially None.
            set_tempo (int): Numeric tempo value that is inputted.
        Returns:
        -------
            set_tempo (int) Numeric tempo value that is going to be set.
        """

        # if buttons not clicked, retain current information
        if not dash.callback_context.triggered:
            return set_tempo

        # Get id of button clicked
        button_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]

        # If button is +, add 1, else if button is -, subtract 1
        if button_id == "tempo-":
            set_tempo -= 1
        elif button_id == "tempo+":
            set_tempo += 1

        return set_tempo


def add_new_track_section(app):
    """ Adds a new track section if 'Add New Track' button is pressed."""
    @app.callback(
        [Output("track_section", "children"),
         Output("track_index", "data")],
        [Input("add_track_button", "n_clicks"),
         Input("track_section", "children")],
        State("track_index", "data"),
        prevent_initial_call=True
    )
    def add_track(n_clicks,  track_container_children, track_index):
        """
        Parameters:
        -----------
            n_clicks (int or None): number button clicked.
            track_section (list): list of html script in track section
            track_index (int): number of track section
        Returns:
        -------
            track_section (list): updated list of html script in track section
                with one additional track section added
            track_index (int): updated number of track section by 1
        """

        # Ignore if no clicks
        if n_clicks is None:
            return track_container_children, track_index

        # Go to next index
        next_index = track_index["index"] + 1

        # New track outline
        one_track = html.Div(
            className="track-tabs-container",
            children=[
                html.Div(
                    className="left-tab-section-container",
                    children=[
                        html.Span(className="track-text",
                                  children=f"Track {next_index}"),
                        html.Div(
                            className="left-row-container",
                            children=[
                                # Play icon button
                                html.Button(
                                    className="left-play-icon-button",
                                    id=f"left_mute_icon_button_{next_index}",
                                    children=[
                                        html.I(className="fa-solid fa-play")],
                                ),
                                # Mute/unmute icon button
                                html.Button(
                                    className="left-mute-icon-button",
                                    id=f"left_mute_icon_button_{next_index}",
                                    children=[
                                        html.I(className="fa-solid fa-volume-xmark")],
                                ),
                                # Trash button
                                html.Button(
                                    className="trash-button",
                                    id=f"left_mute_icon_button_{next_index}",
                                    children=[
                                        html.I(className="fa-solid fa-trash")],
                                )
                            ]
                        ),
                        # Pitch button
                        html.Button(
                            className="pitch-button",
                            id=f"left_mute_icon_button_{next_index}",
                            children="Pitch",
                        )
                    ]
                )
            ]
        )

        # Combine previous track with new track
        track_container_children.append(one_track)

        # Store new index to track index
        track_index["index"] = next_index

        return track_container_children, track_index
