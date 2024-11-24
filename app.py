from flask import Flask, request, jsonify
from resemblyzer import VoiceEncoder
import os
import mimetypes

app = Flask(__name__)

# הגבלת גודל קובץ ל-50MB
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# אתחול VoiceEncoder
encoder = VoiceEncoder()

# רשימת הפורמטים הנתמכים
SUPPORTED_FORMATS = {"audio/wav", "audio/x-wav", "audio/mpeg", "audio/mp3"}

@app.route("/")
def home():
    return "Welcome to the Voice Encoder API! This API supports WAV and MP3 files."

@app.route("/encode", methods=["POST"])
def encode_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file provided. Please upload a file with the key 'file'."}), 400

    file = request.files["file"]

    if file.filename == '':
        return jsonify({"error": "Empty filename. Please provide a valid audio file."}), 400

    # בדיקת סוג הקובץ
    mime_type = mimetypes.guess_type(file.filename)[0]
    if mime_type not in SUPPORTED_FORMATS:
        return jsonify({
            "error": f"Unsupported file format. Supported formats are: {', '.join(SUPPORTED_FORMATS)}"
        }), 400

    # שמירת הקובץ
    file_path = f"/tmp/{file.filename}"
    try:
        file.save(file_path)

        # הפקת Embeddings
        embeddings = encoder.embed_utterance_from_file(file_path)
        return jsonify({"embeddings": embeddings.tolist()})
    except Exception as e:
        print(f"Error processing file: {e}")  # לוג שגיאה
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
    finally:
        # מחיקת הקובץ לאחר עיבוד
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
