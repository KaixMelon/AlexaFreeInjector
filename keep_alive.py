from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Alexa Free Bot is Alive."

@app.route('/video')
def send_video():
    return send_from_directory('.', 'lv_1_1234567.mp4', mimetype='video/mp4')

def keep_alive():
    app.run(host='0.0.0.0', port=8080)
