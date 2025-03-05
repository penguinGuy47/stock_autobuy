from flask import Flask, jsonify
from flask_cors import CORS
from controllers.trade_controller import trade_bp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
app.register_blueprint(trade_bp, url_prefix='/')

if __name__ == '__main__':
    app.run(debug=True)