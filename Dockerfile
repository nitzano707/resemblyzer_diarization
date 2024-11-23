# בחר גרסת Python מתאימה
FROM python:3.11-slim

# התקן GCC ותלויות מערכת אחרות
RUN apt-get update && apt-get install -y \
    gcc \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# הגדר ספריית עבודה
WORKDIR /app

# העתק קבצים
COPY . .

# התקן תלויות Python
RUN pip install --no-cache-dir -r requirements.txt

# הפעל את האפליקציה
CMD ["python", "app.py"]
