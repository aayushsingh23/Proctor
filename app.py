from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-very-secret-key-that-should-be-changed'
socketio = SocketIO(app, async_mode='eventlet')


@app.route('/')
def index():
    """Render the index.html file from the 'templates' folder."""
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    """Handle new client connection."""
    print('Client connected successfully!')


@socketio.on('video_stream')
def handle_video_stream(data):
    """
    Handle video frame data from the client.

    Expected input: data['image'] - base64 image string (in the future).
    """
    print("Received a video frame from the client!")


if __name__ == '__main__':
    print("Starting Flask server on http://127.0.0.1:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
