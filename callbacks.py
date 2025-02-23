import dash
from dash import dcc, html, MATCH, ALL, ctx
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import os
import glob
from dash.exceptions import PreventUpdate
import json
import copy

from LoopMachine import LoopMachine
from assets.layout import Layout

# App callback format
# @app.callback(
#     Ouput(component_id, component_property),
#     Input(component_id, component_property),
#     State(component_id, component_property)
#     def call_back_function(Input, State):
#         return Output

tempo = 100
beats = 4
loop_machine = LoopMachine(tempo, beats)

def get_track_index_button_id():
    """Gets the index and button_id from a triggered dash callback that are indexed."""
    triggered_prop_id = dash.callback_context.triggered[0]["prop_id"]
    #print(triggered_prop_id)
    # Make into dict
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
    # VARYING TEMPO/DURATION??????
    @app.callback(
        [Output("record_button", "className"),
         Output("track_section", "children", allow_duplicate=True)],
        Input("record_button", "n_clicks"),
        prevent_initial_call=True
    )
    def record_pulse(n_clicks):
        """
        Makes the record buttons pulsing red to indicate recording.
        Also stores the track uid in state after recording.
        """
        if n_clicks is None:
            raise PreventUpdate
        if n_clicks % 2 == 0:
            # Stop recording
            loop_machine.stop_recording()
            # Get list of track
            track_list = loop_machine.tracks
            print(track_list)
            # Update the tracks section after recorded track
            updated_track_section = Layout().update_track_section(track_list, loop_machine.latency_compensation_samples)
            return "record-button", updated_track_section
        else:
            # Start recording
            loop_machine.start_recording()
            return "record-button-pulsing pulse", dash.no_update

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
        button_id = get_button_id()

        # If button is +, add 1, else if button is -, subtract 1
        if decrease_tempo and button_id == "tempo-":
            set_tempo -= 1
        elif increase_tempo and button_id == "tempo+":
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
    def generate_pkl_files_checklist(n_clicks):
        """
        Generates a checlist with a list of audio files in the tracks
        directory when the refresh button is clicked.
        """
        loop_file_path = "loops"
        # Get a list of .pkl files
        wave_files_list = glob.glob(os.path.join(loop_file_path, "*.pkl"))

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
        updated_track_section= Layout().update_track_section(track_list, loop_machine.latency_compensation_samples)
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
        updated_track_section= Layout().update_track_section(track_list)
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
        # print(track_index) 
        # print("name:", track.name)
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
        # For recording, clicking is on by default
        # Change this behavior to follow the mute/unmute button
        if button_id == "record_button" and record_n_clicks > 0:
            if mute_unmute_n_clicks is None or mute_unmute_n_clicks % 2 == 0:
                unmute = [
                    html.I(className="fa-solid fa-volume-high"),
                    html.Span(children="Click", className="mute-unmute-click-text")
                ]
                loop_machine.click_is_muted = False 
                return unmute
            else:
                mute = [
                    html.I(className="fa-solid fa-volume-xmark"),
                    html.Span(children="Click", className="mute-unmute-click-text")
                ]
                loop_machine.click_is_muted = True  # Keep muted
                return mute

        # Toggle unmute/mute if not recording
        if mute_unmute_n_clicks is None or mute_unmute_n_clicks % 2 == 0:
            unmute = [
                html.I(className="fa-solid fa-volume-high"),
                html.Span(children="Click", className="mute-unmute-click-text")
            ]
            loop_machine.click_is_muted = False 
            return unmute
        else:
            mute = [
                html.I(className="fa-solid fa-volume-xmark"),
                html.Span(children="Click", className="mute-unmute-click-text")
            ]
            loop_machine.click_is_muted = True  
            return mute

    @app.callback(
        Input("stop_button", "n_clicks"),
        prevent_initial_call=True
    )
    def stop(n_clicks):
        """
        Stops the application if stop button is pressed.
        """
        if n_clicks:
            loop_machine.stop()
    
    @app.callback(
        Output({"type": "pitch_track_text", "index": MATCH}, "children"),  
        [Input({"type": "decrease_track_pitch_button", "index": MATCH}, "n_clicks"),
        Input({"type": "increase_track_pitch_button", "index": MATCH}, "n_clicks")],
        prevent_initial_call=True
    )
    def pitch_changes(decrease_pitch, increase_pitch):
        """
        Increase/decrease pitch changes for a selected track OR the entire loop.
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

        # Apply the pitch shift to the selected track
        track.pitch_shift = pitch_shift
        print(f"Track {track_index}: pitch_shift = {track.pitch_shift}")
        track.apply_pitch_shift_async()

        new_pitch_text = f"Pitch {track.pitch_shift}"
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
            track_list.clear()
            updated_track_section = Layout().update_track_section(track_list)
            return updated_track_section
   
def playhead_callback(app):
    @app.callback(
        Output('playhead', 'style'),
        Input('playhead-interval', 'n_intervals')
    )
    def playhead_update(n_intervals):
        beats = loop_machine.beats_per_loop
        # current beat / beats per loop:
        playhead_position = int((loop_machine.position / loop_machine.frames_per_loop) * beats) / beats
        if playhead_position == 0:
            return {
                "left": "120px"
                }
        return {
            "left": f"calc(120px + ({playhead_position} * (100% - 120px)))",
            "transition": "left 25ms linear"
            }


    def create_waveform(self, track):
        # grab buffered audio from track:
        audio_data = track['track_name'].raw_buffer
        shift_factor = .17 * 44100
        shift_audio = np.roll(audio_data, -shift_factor)
        # set x-axis:
        time = np.linspace(0, len(shift_audio), len(shift_audio))
        # create graph:
        df = pd.DataFrame(
            {"Time": time, "Amplitude": shift_audio.flatten()})
        fig = px.line(df, x="Time", y="Amplitude")
        # remove interactive features:
        fig.update_layout(
            xaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False,
                title_text='',
                visible=False
            ),
            yaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False,
                title_text='',
                visible=False
            ),
            showlegend=False,
            paper_bgcolor='#212529',
            plot_bgcolor='#313539',
            dragmode=False,
            margin=dict(l=0, r=0, t=0, b=0),
            hovermode=False,
        )
        return fig
