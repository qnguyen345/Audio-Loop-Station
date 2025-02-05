import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import os
import glob
from dash.exceptions import PreventUpdate

from track import Track
from loop import Loop
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

    # @app.callback(
    # )
    # def pause_play():
    #     """
    #     Toggles between pause and play buttons. Pause if pause button is clicked.
    #     Play if play button is clicked
    #     """
    #     pass

    # @app.callback(
    # )
    # def mute_unmute():
    #     """
    #     Toggles between mute and unmute buttons. Mute if mute button is clicked.
    #     Unmute if unmute button is clicked
    #     """
    #     pass


def update_layout_callbacks(app):
    """
    Dynamically updates the layout.
    """
    # THIS LOGIC NEEDS TO BE FIXED LATER
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
       

