import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from transformers import pipeline
from googletrans import Translator
import requests
import base64
import time
import threading
from flask import Flask, render_template, request, jsonify
from PIL import Image
from datetime import datetime
import pytz


app = Flask(__name__)

line_notify_token = "YOUR_DEFAULT_LINE_NOTIFY_TOKEN"
last_notification_time = 0
notification_interval = 10  # Default interval in seconds
motion_threshold = 0.3     # Default motion threshold
timezone = pytz.timezone("Asia/Tokyo")

# Setup caption generation pipeline
captioner = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")
# captioner = pipeline("image-to-text", model="nlpconnect/vit-gpt2-image-captioning")

# Function to translate English text to Japanese
def translate_en_to_ja(text):
    translator = Translator()
    translation = translator.translate(text, src='en', dest='ja')
    return translation.text

# Function to send LINE notification with captioned image
def send_line_notify_with_caption(message, image_path, token):
    try:
        url = "https://notify-api.line.me/api/notify"
        headers = {"Authorization": f"Bearer {token}"}
        
        # Generate caption for the image
        image = Image.open(image_path)
        captions = captioner(image, max_new_tokens=50)
        generated_text = captions[0]['generated_text']
        translated_caption = translate_en_to_ja(generated_text)
        
        # Include caption in the message
        payload = {
            "message": f"{message}\n検出内容: {translated_caption}"
        }
        
        files = {"imageFile": open(image_path, "rb")}
        r = requests.post(url, headers=headers, data=payload, files=files)
        return r.status_code
    except Exception as e:
        print(f"Error sending LINE notification with caption: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html', token=line_notify_token, interval=notification_interval, threshold=motion_threshold)

@app.route('/update_settings', methods=['POST'])
def update_settings():
    global line_notify_token, notification_interval, motion_threshold
    line_notify_token = request.form.get('token', line_notify_token)
    notification_interval = int(request.form.get('interval', notification_interval))
    motion_threshold = float(request.form.get('threshold', motion_threshold))
    return jsonify({"status": "success"})

def handle_notification(image_data, timestamp, token):
    image_path = f"static/detected.png"
    
    # Decode base64 image data and save to file
    with open(image_path, "wb") as fh:
        fh.write(base64.b64decode(image_data))

    send_line_notify_with_caption(f"Motion detected at {timestamp}", image_path, token)

@app.route('/notify', methods=['POST'])
def notify():
    global last_notification_time
    current_time = time.time()
    if current_time - last_notification_time < notification_interval:
        return jsonify({"status": "failure", "message": "Notification rate limit exceeded."}), 429

    data = request.get_json()
    image_data = data['image']
    timestamp = datetime.now(timezone).strftime("%Y%m%d-%H%M%S")

    # Start a new thread to handle the notification
    thread = threading.Thread(target=handle_notification, args=(image_data, timestamp, line_notify_token))
    thread.start()

    last_notification_time = current_time
    return jsonify({"status": "success"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)