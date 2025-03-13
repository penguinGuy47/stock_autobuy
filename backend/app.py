from flask import Flask, jsonify
from flask_cors import CORS
from controllers.trade_controller import trade_bp
from routes.split_routes import splits_bp

app = Flask(__name__)
# More specific CORS settings to allow frontend on port 3000 to access backend on port 5000
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
app.register_blueprint(trade_bp, url_prefix='/')
app.register_blueprint(splits_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True, port=5000)