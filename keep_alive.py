from flask import Flask, Response
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Alexa Free Bot is Alive."

@app.route('/video1')
def send_video():
    try:
        with open("lv_1_1234567.mp4", "rb") as f:
            video_data = f.read()
        return Response(
            video_data,
            mimetype="video/mp4",
            headers={
                "Content-Disposition": "inline; filename=lv_1_1234567.mp4",
                "Content-Length": str(len(video_data))
            }
        )
    except FileNotFoundError:
        return "Video not found", 404

def keep_alive():
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
