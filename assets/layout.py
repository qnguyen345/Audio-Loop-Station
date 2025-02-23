import dash_bootstrap_components as dbc
from dash import dcc, html
import dash
import numpy as np
import pandas as pd
import plotly_express as px
import time

from LoopMachine import LoopMachine
tempo = 120
beats = 5
# loop_machine = LoopMachine(tempo, beats)

class Layout:
    def __init__(self, duration=beats, tempo=tempo):
        self.duration = duration
        self.tempo = tempo

    @staticmethod
    def get_top_layout():
        """
        Generates the top section/header of the app.
        This section has the files popup, title, and members/classes info.
        """
        top_layout = [

            # Files section
            # File button popup here: https://dash-bootstrap-components.opensource.faculty.ai/docs/components/modal/
            html.Div(
                className="files-container",
                children=[
                    html.Button(
                        className="files-button",
                        id="files_button",
                        children="Files",
                        n_clicks=0,
                    ),
                ],
            ),
            # Modal for Files
            dbc.Modal(
                className="files-modal",
                id="files_modal",
                is_open=False,
                centered=True,
                backdrop=True,
                scrollable=True,
                children=[

                    # Header/ Modal title
                    dbc.ModalHeader(
                        className="files-modal-header",
                        children=[
                            dbc.ModalTitle(className="modal-files-title",
                                           children="Loop Files"),
                        ]
                    ),

                    # Modal Body
                    dbc.ModalBody(
                        children=[
                            html.Div(
                                className="text-refresh-container",
                                children=[
                                    html.Div(
                                        "Select a loop file to enable/disable:"),
                                    # Refresh Button to refresh tracks directory
                                    # to generate loop checklist
                                    html.Button(
                                        className="refresh-button",
                                        id="refresh_button",
                                        children=[
                                            html.I(className="fa-solid fa-arrows-rotate"
                                                   ),
                                            html.Span(
                                                className="refresh-text",
                                                children="Refresh"
                                            )
                                        ]
                                    )
                                ]
                            ),
                            html.Div(className="checklist-container",
                                     id="checklist_container")
                        ]
                    ),
                    # Close popup button
                    dbc.ModalFooter(
                        dbc.Button(
                            className="close-files-modal",
                            id="close_files_modal",
                            children="Close",
                        )
                    )
                ]
            ),

            # App Title
            html.Div(
                className="title-container",
                children=[
                    html.P(
                        className="title",
                        children="Ostinato Live",
                    )
                ]
            ),

            # Class; members
            html.Div(
                className="members-container",
                children=[
                    html.P(
                        className="member-class-text",
                        children="CS 467 | Winter 2025 ©",
                        style={"padding": "2px",
                               "margin": "0px"}
                    ),
                    html.P(
                        className="member-class-text",
                        children="Arthur Tripp | Quyen Nguyen | Matthew Pennington",
                        style={"padding": "0px",
                               "margin": "0px"}
                    ),
                ]
            )
        ]

        return top_layout

    @staticmethod
    def get_loop_layout():
        """
        Generates the loop layout section."""
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

                            # Trash button
                            html.Button(
                                className="trash-button",
                                id="delete_loop_trash_button",
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

    def get_right_tab_layout(self):
        """
        Generates the right tab layout with the main buttons.
        This section has the record, play/pause, stop, tempo changes,
        auto-trim, delete and save loop buttons.
        """
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

                    # Play/Pause Button and Text
                    html.Button(
                        className="play-pause-button",
                        id="play_pause_button",
                        children=[
                            html.I(className="fa-solid fa-pause"),
                            html.Span(children="Pause",
                                      className="pause-text")
                        ]
                    ),

                    # Mute/Unmute Button and Text
                    html.Button(
                        className="mute-unmute-click-button",
                        id="mute_unmute_click_button",
                        children=[
                            html.I(className="fa-solid fa-volume-high"),
                            html.Span(children="Click",
                                      className="mute-unmute-click-text")
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
                                        value=self.tempo, step=None
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

                    # Duration Input
                    html.Div(
                        className="duration-container",
                        children=[
                            # Duration text
                            html.Span(className="duration-text",
                                      children="Duration (ms): "),
                            # Duration Input
                            dcc.Input(
                                className="duration-input",
                                id="duration_input",
                                type="number",
                                value=self.duration,
                                placeholder="Enter."),
                        ]
                    ),


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

    def update_track_section(self, track_list, input_latency=0):
        """
        Updates the track section for track layout.
        """
        
        # All track section list
        all_tracks_list = []

        # Get mapping of tracks
        track_dict= self.map_tracks(track_list)

        # Generate track section for each track in track_list
        for track_index, track in track_dict.items():
            track_name = track["track_name"]
            pitch_shift = track["pitch_shift"]
            waveform_fig = self.create_waveform(track, input_latency)
            track_section = html.Div(
                className="track-tabs-container",
                children=[
                    html.Div(
                        className="left-tab-section-container",
                        children=[
                            html.Span(className="track-text",
                                      children=f"Track {track_index}:"),
                            # Edit track name 
                            dcc.Input(
                                className="track-name-input",
                                id={"type": "track_name_input",
                                    "index": track_index}, 
                                # Default to original <Untitled> track name
                                value= f"{track_name}", 
                                type="text",
                                debounce=True,
                                autoComplete="off"
                            ),
                            html.Div(
                                className="left-row-container",
                                children=[
                                    # Mute/unmute icon button
                                    html.Button(
                                        className="left-mute-icon-button",
                                        id={"type": "left_mute_icon_button",
                                            "index": track_index},
                                        children = [
                                            html.I(className="fa-solid fa-volume-xmark")],
                                    ),
                                    # Copy icon button
                                    html.Button(
                                        className="copy-button",
                                        id={"type": "copy_button",
                                            "index": track_index},
                                        children=[
                                            html.I(className="fa-solid fa-copy")],
                                    ),
                                    # Trash button
                                    html.Button(
                                        className="trash-button",
                                        id={"type": "trash_button",
                                            "index": track_index},
                                        children = [
                                            html.I(className="fa-solid fa-trash")],
                                    )
                                ]
                            ),
                            # Pitch buttons
                            html.Div(
                                className="pitch-container",
                                children=[
                                    html.Button(
                                        className="decrease-pitch-button",
                                        id={"type": "decrease_track_pitch_button",
                                            "index": track_index},
                                        children="▼"),
                                    html.Span(
                                        className="pitch-text",
                                        id={"type": "pitch_track_text",
                                            "index": track_index},  
                                        children=f"Pitch {pitch_shift}"  
                                    ),
                                    html.Button(
                                        className="increase-pitch-button",
                                        id={"type": "increase_track_pitch_button",
                                            "index": track_index},
                                        children="▲"),
                                ]
                            )
                        ]
                    ),
                    # waveform placement:
                    html.Div([
                        dcc.Graph(id=f"waveform-{track_index}",
                                  figure=waveform_fig,
                                  style={"height": "100%", "width": "100%"},
                                  config={"displayModeBar": False}
                                  )
                        ],
                        className='track-waveform'
                    )
                ]
            )

            # Add track section to list
            all_tracks_list.append(track_section)
        
        # Make it so that the newest track is on the top and oldest track
        # section is on the bottom. Reverse the list to do this.
        return list(reversed(all_tracks_list))

    def map_tracks(self, track_list):
        """
        Maps track to a track index/number.
        """

        # track number keys with track values
        track_dict = {}

        # Make a track dictionary that maps the track to a track number and pitch
        for index, track in enumerate(track_list):
            track_dict[index] = {
            'track_name': track,
            'pitch_shift': track.pitch_shift
        }

        # print("track_list", track_list)  # DEBUG_PRINT
        # print("track_dict", track_dict)  # DEBUG_PRINT
        return track_dict

    
    def create_waveform(self, track, latency_comp=0):
        # grab buffered audio from track:
        audio_data = track['track_name'].raw_buffer
        shifted_audio = np.roll(audio_data, -latency_comp + 150)
        # set x-axis:
        time = np.linspace(0, len(shifted_audio), len(shifted_audio))
        # create graph:
        df = pd.DataFrame(
            {"Time": time, "Amplitude": shifted_audio.flatten()})
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
