from track import Track
import dash_bootstrap_components as dbc
from dash import dcc, html
import dash
import sys
sys.path.append("../")


class Layout:
    def __init__(self, duration, tempo):
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
                            # Pitch button
                            # Pitch buttons
                            html.Div(
                                className="pitch-container",
                                children=[
                                    html.Button(className="decrease-pitch-button",
                                                children="▼"),
                                    html.Span(className="pitch-text",
                                              children="Pitch"),
                                    html.Button(className="increase-pitch-button",
                                                children="▲"),
                                ]
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

    @staticmethod
    def get_add_track_layout():
        """
        Generates the add track layout with the "+ Track" button.
        """
        add_track_layout = html.Div(
            className="add-track-button-container",
            children=[
                html.Button(
                    className="add-track-button",
                    id="add_track_button",
                    children=[
                        html.I(className="fa-solid fa-plus"),
                        "  Track"
                    ],
                )
            ]
        )
        return add_track_layout

    def generate_dummy_track_layout(self, track_num):
        """
        Generates a single dummy track layout when add track is pressed.
        Also generate an initial dummy track of 'Track 1' when app
        is initially launched. These dummy track will later be assigned a track
        UID when a track is recorded.
        """
        dummy_track_layout = [
            html.Div(
                className="track-tabs-container",
                children=[
                    html.Div(
                        className="left-tab-section-container",
                        children=[
                            html.Span(className="track-text",
                                      children=f"Track {track_num}"),
                            html.Div(
                                className="left-row-container",
                                children=[
                                    # Play icon button
                                    html.Button(
                                        className="left-play-icon-button",
                                        children=[
                                            html.I(className="fa-solid fa-play")],
                                    ),
                                    # Mute/unmute icon button
                                    html.Button(
                                        className="left-mute-icon-button",
                                        children=[
                                            html.I(className="fa-solid fa-volume-xmark")],
                                    ),
                                    # Trash button
                                    html.Button(
                                        className="trash-button",
                                        children=[
                                            html.I(className="fa-solid fa-trash")],
                                    )
                                ]
                            ),
                            # Pitch buttons
                            html.Div(
                                className="pitch-container",
                                children=[
                                    html.Button(
                                        className="decrease-pitch-button", children="▼"),
                                    html.Span(className="pitch-text",
                                              children="Pitch"),
                                    html.Button(
                                        className="increase-pitch-button", children="▲"),
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
        
        return dummy_track_layout

    def update_track_section(self, track_list):
        """
        Updates the track section for track layout.
        Also updates the track list.
        """

        # All track section list
        all_tracks_list = []

        # Get mapping of tracks
        track_dict, updated_tracks_list = self.map_tracks(track_list)

        # Generate track section for each track in track_list
        for track_uid, track_num in track_dict.items():
            # track section outline
            track_section = html.Div(
                className="track-tabs-container",
                children=[
                    html.Div(
                        className="left-tab-section-container",
                        children=[
                            html.Span(className="track-text",
                                      children=f"Track {track_num}"),
                            html.Div(
                                className="left-row-container",
                                children=[
                                    # Play icon button
                                    html.Button(
                                        className="left-play-icon-button",
                                        id=f"left_play_icon_button_{track_num}",
                                        children=[
                                            html.I(className="fa-solid fa-play")],
                                    ),
                                    # Mute/unmute icon button
                                    html.Button(
                                        className="left-mute-icon-button",
                                        id=f"left_mute_icon_button_{track_num}",
                                        children=[
                                            html.I(className="fa-solid fa-volume-xmark")],
                                    ),
                                    # Trash button
                                    html.Button(
                                        className="trash-button",
                                        id=f"trash_button_{track_num}",
                                        children=[
                                            html.I(className="fa-solid fa-trash")],
                                    )
                                ]
                            ),
                            # Pitch buttons
                            html.Div(
                                className="pitch-container",
                                children=[
                                    html.Button(
                                        className="decrease-pitch-button", children="▼"),
                                    html.Span(className="pitch-text",
                                              children="Pitch"),
                                    html.Button(
                                        className="increase-pitch-button", children="▲"),
                                ]
                            )
                        ]
                    )
                ]
            )

            # Add track section to list
            all_tracks_list.append(track_section)
        
        # Make it so that the newest track is on the top and oldest track
        # is on the bottom. Reverse the list
        return list(reversed(all_tracks_list)), updated_tracks_list

    def map_tracks(self, track_list):
        """
        Maps track uid to a track number. If there is a "Dummy" value in the
        track_list, then assign it to a uid and then map that to a track number.
        Example:
            track_list = ['Dummy_1', 'Dummy_2', 'Dummy_3', '2389hdiujasd', '9821hkjdasd']
            updated_track_list = ['2389hdiujasd', '9821hkjdasd', 'Dummy_3']
            track_dict = {
                '2389hdiujasd': 1,
                '9821hkjdasd': 2,
                'Dummy_3': 3
            }
        """

        # track number keys with track uid values
        track_dict = {}
        
        # Get lists of uid and Dummy_ variables
        uid_list = [track for track in track_list if not track.startswith("Dummy_")]
        length_uid = len(uid_list)
        dummy_list = [track for track in track_list if track.startswith("Dummy_")]
        length_dummy = len(dummy_list)
        
        # Make an updated track list where the uid replaces the dummy variable
        # Excess dummy variables will be temporarily kept
        if length_dummy > length_uid:
            updated_tracks_list = uid_list + dummy_list[length_uid:]
        else:
            updated_tracks_list = uid_list
        
        # Make a track dictionary that maps uid/Dummy to a track number
        for index, track in enumerate(updated_tracks_list):
            track_dict[track] = index + 1 #Track 1 is the initial track
        # print("track_list", track_list)###DEBUG_PRINT
        # print("track_dict", track_dict) ###DEBUG_PRINT
        # print("updated_tracks_list", updated_tracks_list) ###DEBUG_PRINT
        return track_dict, updated_tracks_list
