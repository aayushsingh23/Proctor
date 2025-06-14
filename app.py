
from flask import Flask, render_template
from flask_socketio import SocketIO

# 1. Initialize the Flask App and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-very-secret-key-that-should-be-changed'

# Use eventlet for async_mode for better performance
socketio = SocketIO(app, async_mode='eventlet')

# 2. Define the main route that serves the HTML page
@app.route('/')
def index():
    """
    This route will render the index.html file from the 'templates' folder.
    """
    return render_template('index.html')

# 3. Define a handler for the 'connect' event
@socketio.on('connect')
def handle_connect():
    """
    This function is called when a new client connects to the server.
    """
    print('Client connected successfully!')

# 4. Define a handler for the 'video_stream' event from the client
@socketio.on('video_stream')
def handle_video_stream(data):
    """
    This function will receive the video frame data from the client.
    For now, we will just print a confirmation message.
    """
    # In the future, 'data['image']' will contain the base64 image string.
    print("Received a video frame from the client!")
    # AI processing will happen here later.

# 5. The main entry point of the application
if __name__ == '__main__':
    """
    Run the app using socketio.run(), not app.run().
    This starts the server with WebSocket support.
    """
    print("Starting Flask server on http://127.0.0.1:5000")
    # Using host='0.0.0.0' makes it accessible on your local network
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)