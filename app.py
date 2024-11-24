from flask import Flask, request, jsonify
from resemblyzer import VoiceEncoder
import os

app = Flask(__name__)

# אתחול VoiceEncoder
encoder = VoiceEncoder()

@app.route("/")
def home():
    return "Welcome to the Voice Encoder API!"

@app.route("/encode", methods=["POST"])
def encode_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    file_path = f"/tmp/{file.filename}"
    file.save(file_path)

    try:
        # יצירת embeddings
        embeddings = encoder.embed_utterance_from_file(file_path)
        return jsonify({"embeddings": embeddings.tolist()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
