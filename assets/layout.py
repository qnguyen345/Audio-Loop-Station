import dash_bootstrap_components as dbc
from dash import dcc, html
import dash


class Layout:
    def __init__(self, tempo, beats):
        self.beats = beats
        self.tempo = tempo

    def generate_icon_button(self, classname, callback_id, icon, index=False):
        """Generates a button with an icon.
        Index is defaulted to False; otherwise, index is need for pattern matching
        callbacks."""
        if index:
            button_id = {"type": str(callback_id), "index": index}
        else:
            button_id = str(callback_id)
        button = html.Button(
            className=str(classname),
            id=button_id,
            children=[html.I(className=str(icon))]
        )
        return button
    
    def generate_text_button(self, classname, callback_id, text, text_classname=False, index=False):
        """Generates a button with text. 
        text_classname is defaulted to False; otherwise, add a text_classname for
        specific css styling to text.
        Index is defaulted to False; otherwise, index is need for pattern matching
        callbacks."""
        if text_classname:
            text_section = html.Span(children=str(text), className=str(text_classname))
        else:
            text_section = html.Span(children=str(text))
        if index:
            button_id = {"type": str(callback_id), "index": index}
        else:
            button_id = str(callback_id)

        button = html.Button(
            className=str(classname),
            id=button_id,
            children=[text_section])
        return button
    
    def generate_icon_and_text_button(self, classname, callback_id, icon, text, text_classname=False):
        """Generates button with icon AND text.
        text_classname is defaulted to False; otherwise, add a text_classname for
        specific css styling to text."""
        if text_classname:
            text_section = html.Span(children=str(text), className=str(text_classname))
        else:
            text_section = html.Span(children=str(text)) 
        button = html.Button(
                className=str(classname),
                id=str(callback_id),
                children=[html.I(className=str(icon)),text_section])
        return button

    def get_top_layout(self):
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
                    self.generate_text_button("files-button", "files_button", "Files")
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
                                    self.generate_icon_and_text_button(
                                        "refresh-button", "refresh_button",
                                        "fa-solid fa-arrows-rotate", "refresh-text",
                                        "Refresh"
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

    def get_loop_layout(self):
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
                            self.generate_icon_button("trash-button",
                                "delete_loop_trash_button", "fa-solid fa-trash")
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
                    self.generate_icon_and_text_button(
                        "record-button", "record_button",
                        "fa-solid fa-microphone", "Record", "record-text"),
                    # Play/Pause Button and Text
                    self.generate_icon_and_text_button(
                        "play-pause-button", "play_pause_button",
                        "fa-solid fa-pause", "Pause", "pause-text"),
                    # Mute/Unmute Button and Text
                    self.generate_icon_and_text_button(
                        "mute-unmute-click-button", "mute_unmute_click_button",
                        "fa-solid fa-volume-high", "Click", "mute-unmute-click-text"),
                    # Stop Button and Text
                    self.generate_icon_and_text_button(
                        "stop-button", "stop_button",
                        "fa-solid fa-stop", "Stop", "stop-text")
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
                                    self.generate_text_button("tempo-button", "tempo-", "-"),
                                    dcc.Input(
                                        className="tempo-input",
                                        id="tempo_input",
                                        type="number",
                                        value=self.tempo, step=None
                                    ),
                                    self.generate_text_button("tempo-button", "tempo+", "+")
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

                    # beats Input
                    html.Div(
                        className="beats-container",
                        children=[
                            # beats text
                            html.Span(className="beats-text",
                                      children="Beats: "),
                            # beats Input
                            dcc.Input(
                                className="beats-input",
                                id="beats_input",
                                type="number",
                                value=self.beats,
                                placeholder="Enter."),
                        ]
                    ),
               
                    # Auto-trimming button
                    self.generate_text_button("auto-trim-button", "auto_trim_button", "Auto-Trim"),

                    # TO BE WORKED ON
                    self.generate_text_button("auto-trim-button", "req2_button", "Req.2 Button"),
                    self.generate_text_button("auto-trim-button", "req3_button", "Req.3 Button"),
                ]
            ),

            html.Div(
                className="right-fifth-row-container",
                children=[

                    # Save button to save loop
                    self.generate_text_button(
                        "delete-loop-button", "delete_loop_button",
                        "Delete Loop", text_classname="delete-loop-text",),

                    # Save button to save loop
                    self.generate_text_button(
                        "save-button", "save_button",
                        "Save Loop", text_classname="save-text",
                    ), 

                ]
            ),
        ]

        return right_layout

    def update_track_section(self, track_list):
        """
        Updates the track section for track layout.
        """
        
        # All track section list
        all_tracks_list = []

        # Get mapping of tracks
        track_dict= self.map_tracks(track_list)

        # Generate track section for each track in track_list
        # Also reverse list here, so that the newest track is on
        # the top and oldest track section is on the bottom.
        for track_index, track in reversed(track_dict.items()):
            track_name = track["track_name"]
            pitch_shift = track["pitch_shift"]
            # track section outline
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
                                    self.generate_icon_button("left-mute-icon-button", "left_mute_icon_button",
                                                               "fa-solid fa-volume-xmark", track_index),
                                    # Copy icon button
                                    self.generate_icon_button("copy-button", "copy_button",
                                                               "fa-solid fa-copy", track_index),
                                    # Trash button
                                    self.generate_icon_button("trash-button", "trash_button",
                                                               "fa-solid fa-trash", track_index)
                                ]
                            ),
                            # Pitch buttons
                            html.Div(
                                className="pitch-container",
                                children=[
                                    self.generate_text_button("decrease-pitch-button", 
                                                              "decrease_track_pitch_button",
                                                              "▼", index=track_index),
                                    html.Span(
                                        className="pitch-text",
                                        id={"type": "pitch_track_text",
                                            "index": track_index},  
                                        children=f"Pitch {pitch_shift}"  
                                    ),
                                    self.generate_text_button("increase-pitch-button", 
                                                              "increase_track_pitch_button",
                                                              "▲", index=track_index),
                                ]
                            )
                        ]
                    )
                ]
            )

            # Add track section to results list
            all_tracks_list.append(track_section)
        
        return all_tracks_list

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
