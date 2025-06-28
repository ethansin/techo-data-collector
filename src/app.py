import os
import requests
import time
from flask import Flask, request, send_from_directory
import dropbox
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

class DropboxTokenCache:
    def __init__(self):
        self.access_token = None
        self.expires_at = 0

    def get_token(self):
        if time.time() >= self.expires_at:
            refresh_token = os.getenv("DROPBOX_REFRESH_TOKEN")
            client_id = os.getenv("DROPBOX_CLIENT_ID")
            client_secret = os.getenv("DROPBOX_CLIENT_SECRET")

            response = requests.post("https://api.dropbox.com/oauth2/token", data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": client_id,
                "client_secret": client_secret
            })
            response.raise_for_status()
            token_data = response.json()

            self.access_token = token_data["access_token"]
            self.expires_at = time.time() + token_data.get("expires_in", 14400) - 60

        return self.access_token

dropbox_token_cache = DropboxTokenCache()

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
        token = DropboxTokenCache.get_token()
        dbx = dropbox.Dropbox(token)
        dbx.files_upload(photo.read(), dropbox_path)
        return {"message": "Uploaded successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(debug=True)