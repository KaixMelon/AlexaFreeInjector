from flask import Flask, send_from_directory
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Alexa Free Bot is Alive."

@app.route('/videoJuly15')
def send_video():
    return send_from_directory('.', 'lv_0_20250715094318.mp4', mimetype='video/mp4')

def keep_alive():
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
