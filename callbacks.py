import dash
from dash import dcc, html, MATCH, ALL, ctx
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import os
import glob
from dash.exceptions import PreventUpdate
import json

from track import Track
from LoopMachine import LoopMachine
from assets.layout import Layout

# App callback format
# @app.callback(
#     Ouput(component_id, component_property),
#     Input(component_id, component_property),
#     State(component_id, component_property)
#     def call_back_function(Input, State):
#         return Output

loop_machine = LoopMachine()


def button_callbacks(app):
    """Callbacks for button animations and interactions."""
    # VARYING TEMPO/DURATION??????
    @app.callback(
        [Output("record_button", "className"),
         Output("stored_track_list", "data", allow_duplicate=True),
         Output("track_section", "children", allow_duplicate=True)],
        Input("record_button", "n_clicks"),
        [State("stored_track_list", "data"),
         State("stored_duration", "data"),
         State("stored_tempo", "data")],
        prevent_initial_call=True
    )
    def record_pulse(n_clicks, track_list, duration, tempo):
        """
        Makes the record buttons pulsing red to indicate recording.
        Also stores the track uid in state after recording.
        """
        if n_clicks is None:
            raise PreventUpdate
        if n_clicks % 2 == 0:
            # Stop recording
            loop_machine.stop_recording()
            return "record-button", dash.no_update, dash.no_update
        else:
            # Start recording
            loop_machine.start_recording()

            recording_track = Track(duration)
            # Add uid of recording track to track list
            track_list.append(recording_track.get_uid())
            # Update the tracks section after recorded track
            updated_track_section, updated_track_list = Layout(
                duration, tempo).update_track_section(track_list)
            return "record-button-pulsing pulse", updated_track_list, updated_track_section,

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
        """

        # if buttons not clicked, retain current information
        if not dash.callback_context.triggered:
            raise PreventUpdate

        # Get id of button clicked
        button_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]

        # If button is +, add 1, else if button is -, subtract 1
        if button_id == "tempo-":
            set_tempo -= 1
        elif button_id == "tempo+":
            set_tempo += 1

        return set_tempo

    @app.callback(
        Output("files_modal", "is_open"),
        [Input("files_button", "n_clicks"),
         Input("close_files_modal", "n_clicks")],
        [State("files_modal", "is_open")],
    )
    def toggle_files_modal(n1, n2, is_open):
        """
        Opens a popup when files button is clicked.
        """
        if n1 or n2:
            return not is_open
        return is_open

    @app.callback(
        Output("checklist_container", "children"),
        Input("refresh_button", "n_clicks")
    )
    def generate_wav_files_checklist(n_clicks):
        """
        Generates a checlist with a list of audio files in the tracks
        directory when the refresh button is clicked.
        """
        loop_file_path = "tracks"
        # Get a list of .wav files
        wave_files_list = glob.glob(os.path.join(loop_file_path, "*.wav"))

        # Get file names of audio files without path
        filenames = [os.path.basename(file) for file in wave_files_list]

        # Create a checklist
        checklist = dbc.Checklist(
            options=[{"label": file, "value": file} for file in filenames],
            value=[],
            inline=False,
        )

        return checklist

    @app.callback(
        Output("play_pause_button", "children"),
        Input("play_pause_button", "n_clicks"),
        prevent_initial_call=True
    )
    def pause_play_loop(n_clicks):
        """
        Toggles between pause and play buttons for LOOP.
        Pause loop if pause button is clicked.
        Play loop if play button is clicked.
        """

        # Initial and even clicks are pause
        if n_clicks is None or n_clicks % 2 == 0:
            pause = [
                html.I(className="fa-solid fa-pause"),
                html.Span(children="Pause", className="pause-text")
            ]
            return pause
        else:
            # Odd clicks are play
            play = [
                html.I(className="fa-solid fa-play"),
                html.Span(children="Play",
                          className="play-text")
            ]
            return play

    @app.callback(
        Output({"type": "left_play_icon_button", "index": MATCH}, "children"),
        Input({"type": "left_play_icon_button", "index": MATCH}, "n_clicks"),
        prevent_initial_call=True
    )
    def pause_play_track(n_clicks):
        """
        Toggles between pause and play buttons for TRACKS.
        Pauses track if pause button is clicked.
        Plays track if play button is clicked.
        DOES NOT TOGGLE for Dummy_{index} track sections or track sections
        with no recorded tracks.
        """
        # Initial and even clicks are pause
        if n_clicks is None or n_clicks % 2 == 0:
            pause = [
                html.I(className="fa-solid fa-pause")
            ]
            return pause
        else:
            # Odd clicks are play
            play = [
                html.I(className="fa-solid fa-play"),
            ]
            return play

    @app.callback(
        Output({"type": "left_mute_icon_button", "index": MATCH}, "children"),
        Input({"type": "left_mute_icon_button", "index": MATCH}, "n_clicks"),
        prevent_initial_call=True
    )
    def mute_unmute_track(n_clicks):
        """
        Toggles between mute and unmute buttons for TRACKS.
        Mutes track if mute button is clicked.
        Unmutes track if unmute button is clicked.
        DOES NOT TOGGLE for Dummy_{index} track sections or track sections
        with no recorded tracks.
        """
        # Initial and even clicks are mutes
        if n_clicks is None or n_clicks % 2 == 0:
            mute = [
                html.I(className="fa-solid fa-volume-xmark")
            ]
            return mute
        else:
            # Odd clicks are unmutes
            unmute = [
                html.I(className="fa-solid fa-volume-high"),
            ]
            return unmute

    # VARYING TEMPO/DURATION??????
    @app.callback(
        [Output("track_section", "children", allow_duplicate=True),
         Output("stored_track_list", "data", allow_duplicate=True)],
        Input({"type": "trash_button", "index": ALL}, "n_clicks"),
        State("stored_track_list", "data"),
        prevent_initial_call=True
    )
    def delete_track(n_clicks, track_list):
        """
        Toggles between mute and unmute buttons for TRACKS.
        Mutes track if mute button is clicked.
        Unmutes track if unmute button is clicked.
        DOES NOT TOGGLE for Dummy_{index} track sections or track sections
        with no recorded tracks.
        """
        if not any(n_clicks):
            raise PreventUpdate
        # Get the index of the button that was clicked, triggered_index
        # returns str not a dict value
        triggered_index = dash.callback_context.triggered[0]["prop_id"].split(".")[
            0]
        track_index = int(triggered_index.split('{"index":')[-1].split(",")[0])
        # Remove the track from track_list
        track_list.pop(track_index-1)
        # Update the track sections
        updated_track_section, updated_track_list = Layout().update_track_section(track_list)
        return updated_track_section, updated_track_list

    @app.callback(
        Output("mute_unmute_click_button", "children"),
        Input("mute_unmute_click_button", "n_clicks"),
        prevent_initial_call=True
    )
    def mute_unmute_click(n_clicks):
        """
        Toggles between mute and unmute buttons for clicks.
        Mute click if mute button is clicked.
        Unmute click if unmute button is clicked
        """
        # Even clicks or initial click is mute
        if n_clicks is None or n_clicks % 2 == 0:
            mute = [
                html.I(className="fa-solid fa-volume-xmark"),
                html.Span(children="Click",
                          className="mute-unmute-click-text")
            ]
            return mute

        # Odd clicks are unmute
        else:
            unmute = [
                html.I(className="fa-solid fa-volume-high"),
                html.Span(children="Click",
                          className="mute-unmute-click-text")
            ]
            return unmute


def update_layout_callbacks(app):
    """
    Dynamically updates the layout.
    """
    # VARYING TEMPO/DURATION??????
    @app.callback(
        [Output("stored_duration", "data"),
         Output("stored_tempo", "data"),
         Output("track_section", "children")],
        [Input("duration_input", "value"),
         Input("tempo_input", "value")],
        State("stored_track_list", "data")
    )
    def update_layout(duration, tempo, track_list):
        """
        Sets the tempo and duration and stores them.
        Also updates the layout when track_list changes.
        """
        # If track list is initialize to 'Dummy_1',
        # make an initial blank 'Track 1' outline
        if len(track_list) == 1 and track_list[0] == "Dummy_1":
            return duration, tempo, Layout(duration, tempo).generate_dummy_track_layout(1)
        else:
            updated_track_section, updated_track_list = Layout(
                duration, tempo).update_track_section(track_list)
            return duration, tempo, updated_track_section

    @app.callback(
        [Output("track_section", "children", allow_duplicate=True),
         Output("stored_track_list", "data", allow_duplicate=True)],
        [Input("add_track_button", "n_clicks")],
        [State("track_section", "children"),
         State("stored_track_list", "data"),
         State("duration_input", "value"),
         State("tempo_input", "value")],
        prevent_initial_call='initial_duplicate'
    )
    def add_track(n_clicks, track_section, track_list, duration, tempo):
        """
        Adds a new dummy track section when '+ Track' button is pressed.
        The dummy track section is assigned to a track UID after a track is
        recorded.
        """
        if n_clicks is None:
            raise PreventUpdate
        # If '+ Track"is clicked, update track layout with new dummy track section
        latest_track = len(track_list) + 1
        updated_track_section = Layout(
            duration, tempo).generate_dummy_track_layout(latest_track)
        track_section = updated_track_section + track_section
        track_list.append(f"Dummy_{latest_track}")
        # print("added_track_list", track_list)# DEBUG_PRINT
        return track_section, track_list
