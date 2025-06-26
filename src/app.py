import os
import time
from flask import Flask, request, send_from_directory
import dropbox
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

DROPBOX_TOKEN = os.getenv("DROPBOX_TOKEN")
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/upload", methods=["POST"])
def upload():
    photo = request.files.get("photo")
    if not photo:
        return {"error": "No file uploaded"}, 400

    timestamp = int(time.time())
    filename = f"photo_{timestamp}.jpg"
    dropbox_path = f"/techo-scanner-data/{filename}"

    try:
        dbx.files_upload(photo.read(), dropbox_path)
        return {"message": "Uploaded successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(debug=True)