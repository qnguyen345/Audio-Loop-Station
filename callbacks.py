import dash
from dash import html, MATCH, ALL
from dash.dependencies import Input, Output, State
import os
import glob
from dash.exceptions import PreventUpdate
import json
import copy
from LoopMachine import LoopMachine
from assets.layout import Layout

bpl = 5
beats = 120
loop_machine = LoopMachine(bpm=beats, beats_per_loop=bpl)


def get_track_index_button_id():
    """Gets the index and button_id from a triggered dash callback
    that are indexed."""
    triggered_prop_id = dash.callback_context.triggered[0]["prop_id"]
    # Make into dictonary
    button_id = triggered_prop_id.split(".")[0]
    button_id_dict = json.loads(button_id.replace("'", '"'))

    # get the index and (button" type
    track_index = int(button_id_dict["index"])
    button_id = str(button_id_dict["type"])
    return track_index, button_id


def get_button_id():
    """Gets the button_id for triggered dash callbacks that are not indexed."""
    triggered_prop_id = dash.callback_context.triggered[0]["prop_id"]
    button_id = triggered_prop_id.split(".")[0]
    return button_id


def button_callbacks(app):
    """Callbacks for button animations and interactions."""
    @app.callback(
        [Output("record_button", "className"),
         Output("track_section", "children", allow_duplicate=True)],
        Input("record_button", "n_clicks"),
        prevent_initial_call=True
    )
    def record_pulse(n_clicks):
        """
        Records the audio when the "Record" button is pressed.
        """
        if n_clicks is None:
            raise PreventUpdate
        if n_clicks % 2 == 0:
            # Stop recording
            loop_machine.stop_recording()
            # Get list of track & update track section
            track_list = loop_machine.tracks
            updated_track_section = Layout().update_track_section(
                track_list, loop_machine.latency_compensation_samples)
            return "record-button", updated_track_section
        else:
            # Start recording
            loop_machine.start_recording()
            return "record-button-pulsing pulse", dash.no_update

    @app.callback(
        Output("play_pause_button", "children"),
        Input("play_pause_button", "n_clicks"),
        prevent_initial_call=True
    )
    def pause_play_loop(n_clicks):
        """
        Toggles between pause and play buttons for the LOOP.
        Pause loop if pause button is clicked.
        Play loop if play button is clicked.
        """
        # Initial and even clicks are pause
        if n_clicks is None or n_clicks % 2 == 0:
            loop_machine.is_playing = not loop_machine.is_playing
            pause = [
                html.I(className="fa-solid fa-pause"),
                html.Span(children="Pause", className="pause-text")
            ]
            return pause
        else:
            # Odd clicks are play
            loop_machine.is_playing = not loop_machine.is_playing
            play = [
                html.I(className="fa-solid fa-play"),
                html.Span(children="Play",
                          className="play-text")
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
        """
        track_index, _ = get_track_index_button_id()
        track = loop_machine.tracks[track_index]
        # odd clicks are mutes
        if n_clicks % 2 != 0:
            track.is_muted = True
            mute = [
                html.I(className="fa-solid fa-volume-high")
            ]
            return mute
        else:
            # even clicks are unmutes
            track.is_muted = False
            unmute = [
                html.I(className="fa-solid fa-volume-xmark"),
            ]
            return unmute

    @app.callback(
        Output("track_section", "children", allow_duplicate=True),
        Input({"type": "copy_button", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    def copy_track(n_clicks):
        """Copies the track to the latest track section."""
        if not any(n_clicks):
            raise PreventUpdate
        track_index, _ = get_track_index_button_id()
        track_list = loop_machine.tracks
        track = track_list[track_index]
        # copy track
        track_list.append(copy.copy(track))
        # Update the track sections
        updated_track_section = Layout().update_track_section(
            track_list, loop_machine.latency_compensation_samples)
        return updated_track_section

    @app.callback(
        Output("track_section", "children", allow_duplicate=True),
        Input({"type": "trash_button", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    def delete_track(n_clicks):
        """
        Deletes the track.
        """
        if not any(n_clicks):
            raise PreventUpdate
        track_index, _ = get_track_index_button_id()
        track_list = loop_machine.tracks
        # Remove the track from track_list
        track_list.pop(track_index)
        # Update the track sections
        updated_track_section = Layout().update_track_section(track_list)
        return updated_track_section

    @app.callback(
        Output({"type": "track_name_input", "index": MATCH}, "value"),
        Input({"type": "track_name_input", "index": MATCH}, "value"),
        prevent_initial_call=True
    )
    def update_track_name(new_name):
        """Updates the track name to whatever the user input."""
        # get track_index
        track_index, _ = get_track_index_button_id()
        # Update track name in track list
        track = loop_machine.tracks[track_index]
        track.name = new_name
        return str(new_name)

    @app.callback(
        Output("mute_unmute_click_button", "children"),
        [Input("mute_unmute_click_button", "n_clicks"),
         Input("record_button", "n_clicks")],
        prevent_initial_call=True
    )
    def mute_unmute_click(mute_unmute_n_clicks, record_n_clicks):
        """
        Toggles between mute and unmute buttons for clicks.
        """
        button_id = get_button_id()
        unmute = [html.I(className="fa-solid fa-volume-high"),
                  html.Span(children="Click",
                            className="mute-unmute-click-text")]
        mute = [html.I(className="fa-solid fa-volume-xmark"),
                html.Span(children="Click",
                          className="mute-unmute-click-text")]
        # For recording, clicking is initially on by default
        # Change this behavior to follow the mute/unmute button
        if button_id == "record_button" and record_n_clicks > 0:
            if mute_unmute_n_clicks is None or mute_unmute_n_clicks % 2 != 0:
                loop_machine.click_is_muted = False
                return unmute
            else:
                loop_machine.click_is_muted = True
                return mute
        # Toggle unmute/mute directly if not recording
        if mute_unmute_n_clicks is None or mute_unmute_n_clicks % 2 != 0:
            loop_machine.click_is_muted = False
            return unmute
        else:
            loop_machine.click_is_muted = True
            return mute

    @app.callback(
        Output({"type": "pitch_track_text", "index": MATCH}, "children"),
        [Input({"type": "decrease_track_pitch_button", "index": MATCH},
               "n_clicks"),
         Input({"type": "increase_track_pitch_button", "index": MATCH},
               "n_clicks")],
        prevent_initial_call=True
    )
    def pitch_changes(decrease_pitch, increase_pitch):
        """
        Increase/decrease pitch changes for a selected track OR the entire
        loop.
        """
        if not dash.callback_context.triggered:
            raise PreventUpdate

        track_index, button_id = get_track_index_button_id()
        # Get initial pitch shift
        track = loop_machine.tracks[track_index]
        pitch_shift = track.pitch_shift
        # Decrease pitch by 1
        if decrease_pitch and button_id == "decrease_track_pitch_button":
            pitch_shift -= 1
        # Increase pitch by 1
        elif increase_pitch and button_id == "increase_track_pitch_button":
            pitch_shift += 1

        # Set the new the pitch shift to the selected track
        track.pitch_shift = pitch_shift
        track.apply_effects_async()

        new_pitch_text = f"Pitch: {track.pitch_shift}"
        return new_pitch_text

    @app.callback(
        Output("track_section", "children", allow_duplicate=True),
        [Input("delete_loop_trash_button", "n_clicks"),
         Input("delete_loop_button", "n_clicks")],
        prevent_initial_call=True
    )
    def delete_loop(trash_icon_clicks, delete_button_clicks):
        """Deletes the current loop."""
        button_id = get_button_id()
        if "delete_loop_trash_button" == button_id or "delete_loop_button" == button_id:
            track_list = loop_machine.tracks
            # Deletes everything in the list by clearing it
            track_list.clear()
            updated_track_section = Layout().update_track_section(track_list)
            return updated_track_section

    @app.callback(
        Output("track_section", "children", allow_duplicate=True),
        Input("track_buffer_poll", "n_intervals"),
        prevent_initial_call=True
    )
    def refresh_ui(*_):
        """Refreshes the track section"""
        if app.layout['track_buffer_modified'].data:
            app.layout['track_buffer_modified'].data = False
            updated_track_section = Layout().update_track_section(
                loop_machine.tracks, loop_machine.latency_compensation_samples)
            return updated_track_section
        else:
            return dash.no_update

    def trigger_on_track_buffer_modified(track):
        """Keeps track of track buffer if it is modified or not."""
        current_value = app.layout['track_buffer_modified'].data
        app.layout['track_buffer_modified'].data = True

    loop_machine.on_track_buffer_modified = trigger_on_track_buffer_modified


def offset_callbacks(app):
    """Callbacks for beats per loop, bpm, and latency offset."""
    @app.callback(
        Output("bpl_text", "children", allow_duplicate=True),
        [Input("increase_bpl_button", "n_clicks"),
            Input("decrease_bpl_button", "n_clicks")],
        prevent_initial_call=True
    )
    def set_bpl(increase_bpl, decrease_bpl):
        """
        Updates beats per loop (bpl) of the loop machine from
        increase/decrease buttons.
        """
        if not dash.callback_context.triggered:
            raise PreventUpdate

        button_id = get_button_id()
        # Get initial beats per loop
        bpl = loop_machine.beats_per_loop
        # Decrease bpl by 1
        if decrease_bpl and button_id == "decrease_bpl_button":
            # If bpl goes to negative, set as 0
            if bpl >= 0:
                bpl -= 1
            else:
                bpl = 0
        # Increase bpl by 1
        elif increase_bpl and button_id == "increase_bpl_button":
            bpl += 1

        # Sets the new BPL in the loop machine
        loop_machine.set_beats_per_loop(bpl)
        return f"Beats Per Loop: {bpl}"

    @app.callback(
        Output("bpm_text", "children", allow_duplicate=True),
        [Input("increase_bpm_button", "n_clicks"),
            Input("decrease_bpm_button", "n_clicks")],
        prevent_initial_call=True
    )
    def update_bpm(increase_bpm, decrease_bpm):
        """
        Updates the BPM of the loop machine from increase/decrease buttons.
        """
        if not dash.callback_context.triggered:
            raise PreventUpdate

        button_id = get_button_id()
        # Get initial bpm
        bpm = loop_machine.bpm
        # Decrease bpm by 10
        if decrease_bpm and button_id == "decrease_bpm_button":
            bpm -= 10
        # Increase bpm by 10
        elif increase_bpm and button_id == "increase_bpm_button":
            bpm += 10

        # Sets the new BPM in the loop machine
        loop_machine.set_bpm(bpm)
        return f"BPM: {bpm}"

    @app.callback(
        [Output("track_section", "children", allow_duplicate=True),
         Output("latency_text", "children")],
        [Input("increase_latency_button", "n_clicks"),
         Input("decrease_latency_button", "n_clicks")],
        prevent_initial_call=True
    )
    def set_latency(increase_latency, decrease_latency):
        """
        Sets the latency of the loop machine from increase/decrease buttons.
        """
        if not dash.callback_context.triggered:
            raise PreventUpdate

        button_id = get_button_id()
        # Get initial latency
        latency_compensation_samples = loop_machine.latency_compensation_samples
        latency = latency_compensation_samples / loop_machine.rate
        # Decrease latency by 0.01
        if decrease_latency and button_id == "decrease_latency_button":
            latency -= 0.01
        # Increase bpm offset by 0.01
        elif increase_latency and button_id == "increase_latency_button":
            latency += 0.01
        
        # Calculate new latency compensation samples with new latency
        new_latency_comp = int(float(latency) * loop_machine.rate)
        loop_machine.latency_compensation_samples = new_latency_comp
        track_list = loop_machine.tracks
        updated_track_section = Layout().update_track_section(track_list,
                                                              new_latency_comp)
        return updated_track_section, "Latency (s) {:.2f}:".format(latency)

    @app.callback(
        Output({"type": "offset_beats_text", "index": MATCH}, "children"),
        [Input({"type": "decrease_offset_beats_button", "index": MATCH},
               "n_clicks"),
         Input({"type": "increase_offset_beats_button", "index": MATCH},
               "n_clicks")],
        prevent_initial_call=True
    )
    def set_offset_beats(decrease_beats, increase_beats):
        """
        Increases/ decreases offsets the beats for a specific track.
        """
        if not dash.callback_context.triggered:
            raise PreventUpdate

        track_index, button_id = get_track_index_button_id()
        # Get initial offset beats
        track = loop_machine.tracks[track_index]
        offset_beats = track.offset_beats
        # Decrease beats offset by 0.5
        if decrease_beats and button_id == "decrease_offset_beats_button":
            offset_beats -= 0.5
        # Increase beats offset by 0.5
        elif increase_beats and button_id == "increase_offset_beats_button":
            offset_beats += 0.5

        # Set the new beats offset to the selected track
        track.offset_beats = offset_beats
        track.apply_effects_async()
        new_beats_text = f"Offset Beats: {track.offset_beats}"
        return new_beats_text


def load_save(app):
    """Callbacks for loading and saving a loop."""
    @app.callback(
        Output("save_button", "children"),
        Input("save_button", "n_clicks"),
    )
    def save_loop(n_clicks):
        """Saves current loop in 'loops' directory."""
        button_id = get_button_id()
        if "save_button" == button_id:
            loop_machine.save()
        return dash.no_update

    @app.callback(
        [Output("track_section", "children", allow_duplicate=True),
         Output("files_modal", "is_open"),
         Output("bpl_text", "children", allow_duplicate=True),
         Output("bpm_text", "children", allow_duplicate=True),
         Output("latency_text", "children", allow_duplicate=True),
         Output("pkl_files", "options")],
        [Input("files_button", "n_clicks"),
         Input("load_files_modal", "n_clicks")],
        [State("files_modal", "is_open"),
         State("pkl_files", "value")],
        prevent_initial_call=True
    )
    def load_files(n1, n2, is_open, filename):
        """
        Opens and closes the files modal.
        Also loads the selected .pkl file and displays the track
        in track section.
        """
        button_id = get_button_id()
        if button_id == "files_button":
            # Get a list of .pkl files
            wave_files_list = glob.glob(os.path.join("loops", "*.pkl"))
            # Get file names of audio files without path
            filenames = [os.path.basename(file) for file in wave_files_list]
            filenames = sorted(filenames, reverse=True)
            # Create a radio button for each file
            options = [{"label": file, "value": file} for file in filenames]
            # Open modal with refreshed .pkl list
            return dash.no_update, True, dash.no_update, dash.no_update, dash.no_update, options
        # Load selected .pkl file if 'load and close' button is pressed
        if button_id == "load_files_modal":
            loop_machine.load(filename)
            # Get tracks from loaded file and update display
            track_list = loop_machine.tracks
            latency_comp = loop_machine.latency_compensation_samples
            bpl = loop_machine.beats_per_loop
            bpm = loop_machine.bpm
            latency = latency_comp / loop_machine.rate
            updated_track_section = Layout().update_track_section(track_list, latency_comp)
            return updated_track_section, False, f"Beats Per Loop: {bpl}", f"BPM: {bpm}", "Latency (s): {:.2f}".format(latency), dash.no_update
        return dash.no_update, is_open, dash.no_update, dash.no_update, dash.no_update, dash.no_update,


def playhead_callback(app):
    """Callbacks for playhead animation."""
    @app.callback(
        Output('playhead', 'style'),
        Input('playhead-interval', 'n_intervals')
    )
    def playhead_update(n_intervals):
        """Updates the playhead position."""
        beats = loop_machine.beats_per_loop
        # current beat / beats per loop:
        playhead_position = int(
            (loop_machine.position / loop_machine.frames_per_loop) * beats) / beats
        if playhead_position == 0:
            return {"left": "260px"}
        return {"left": f"calc(260px + ({playhead_position} * (100% - 260px)))"}
