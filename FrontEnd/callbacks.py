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
            # Pulsing for clicked button
            return "record-button"
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