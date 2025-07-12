from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment
load_dotenv()

app = Flask(
    __name__,
    static_folder='../client/static',
    template_folder='../client/templates'
)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
CORS(app)

# Register your Blueprint
from routes import routes
app.register_blueprint(routes)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
