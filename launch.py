from app import app
import threading
import webview


def run_program():
    app.run('127.0.0.1', port=8050)

if __name__ == "__main__":
    threading.Thread(target=run_program, daemon=True).start()
    
    webview.create_window('Ostinato Live | Audio Loop Station',
                          'http://127.0.0.1:8050',
                          height=800, 
                          width=1300,
                          maximized=True)
    webview.start()
    
    