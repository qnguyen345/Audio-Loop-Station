import dash
from dash import dcc, html
import dash_bootstrap_components as dbc


def get_top_layout():

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
                    children=["TO BE IMPLEMENTED"
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
