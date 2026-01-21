import os
from flask import Flask
from dotenv import load_dotenv

# Import Blueprints
from routes.auth import auth_bp
from routes.main import main_bp
from routes.dashboard import dashboard_bp

# Load configuration
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'DefaultKey')

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(dashboard_bp)

if __name__ == '__main__':
    # Ensure database folder exists
    from utils import RECORD_DIR
    if not os.path.exists(RECORD_DIR):
        os.makedirs(RECORD_DIR)
        
    app.run(debug=True)