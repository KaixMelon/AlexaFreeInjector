from flask import Flask, send_from_directory
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Alexa Free Bot is Alive."

@app.route('/video')
def send_video():
    return send_from_directory('.', 'lv_1_1234567.mp4', mimetype='video/mp4')

@app.route('/ping')
def ping():
    return "Pong"

def keep_alive():
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
