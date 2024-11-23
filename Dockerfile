# בחר גרסת Python מתאימה
FROM python:3.11-slim

# התקן FFmpeg ותלויות מערכת
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# הגדר ספריית עבודה
WORKDIR /app

# העתק קבצים
COPY . .

# התקן תלויות Python
RUN pip install --no-cache-dir -r requirements.txt

# הפעל את האפליקציה
CMD ["python", "app.py"]
