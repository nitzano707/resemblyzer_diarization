from flask import Flask, request, jsonify
from resemblyzer import VoiceEncoder
from sklearn.cluster import KMeans
from pydub import AudioSegment
import numpy as np
import librosa
import os

app = Flask(__name__)

def convert_to_wav(input_path, output_path):
    """
    ממיר קובץ אודיו לפורמט WAV.
    """
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)  # מונו עם תדר דגימה של 16kHz
    audio.export(output_path, format="wav")

def diarize_speakers(audio_path, window_size=2.0, step_size=1.0, n_speakers=2):
    """
    ביצוע זיהוי דוברים עם חותמות זמן.
    """
    encoder = VoiceEncoder()

    # אם הקובץ אינו בפורמט WAV, המרה ל-WAV
    if not audio_path.endswith(".wav"):
        temp_path = "/tmp/converted_audio.wav"
        convert_to_wav(audio_path, temp_path)
        audio_path = temp_path

    # טען את קובץ האודיו
    wav, sr = librosa.load(audio_path, sr=16000)

    # חיתוך האודיו למקטעים
    frames_per_window = int(sr * window_size)
    frames_per_step = int(sr * step_size)

    segments = [
        wav[i:i + frames_per_window]
        for i in range(0, len(wav) - frames_per_window, frames_per_step)
    ]

    # הפקת הטבעות קוליות
    embeddings = np.array([encoder.embed_utterance(segment) for segment in segments])

    # קיבוץ (Clustering)
    kmeans = KMeans(n_clusters=n_speakers, random_state=0).fit(embeddings)
    labels = kmeans.labels_

    # יצירת תוצאות עם חותמות זמן
    diarization_results = []
    for i, label in enumerate(labels):
        start_time = i * step_size
        end_time = start_time + window_size
        diarization_results.append({
            "speaker": f"Speaker {label}",
            "start_time": start_time,
            "end_time": end_time
        })

    # מחיקת קובץ זמני
    if audio_path == "/tmp/converted_audio.wav":
        os.remove(audio_path)

    return diarization_results

@app.route("/diarize", methods=["POST"])
def diarize():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    file_path = f"/tmp/{audio_file.filename}"
    audio_file.save(file_path)

    # ניתוח הדוברים
    try:
        n_speakers = int(request.form.get("n_speakers", 2))  # מספר הדוברים המשוער
        results = diarize_speakers(file_path, n_speakers=n_speakers)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
