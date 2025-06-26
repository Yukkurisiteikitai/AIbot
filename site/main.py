import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from functools import wraps
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)


load_dotenv()

# 設定
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', 'your-google-client-id')
# ルート定義
@app.route('/')
def index():
    return render_template('index.html', client_id=GOOGLE_CLIENT_ID)



if __name__ == '__main__':
    app.run(debug=True, port=8010)