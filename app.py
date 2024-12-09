import requests
import fitz  # PyMuPDF
from google.cloud import storage
from datetime import datetime
import tempfile
import os
from flask import Flask

app = Flask(__name__)

def get_nyt_pdf_url():
    today = datetime.now()
    year = today.year
    month = f"{today.month:02d}"
    day = f"{today.day:02d}"
    return f"https://static01.nyt.com/images/{year}/{month}/{day}/nytfrontpage/scan.pdf"

def download_pdf(url):
    response = requests.get(url)
    response.raise_for_status()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(response.content)
        return temp_pdf.name

def convert_pdf_to_image(pdf_path, local_image_path):
    pdf_document = fitz.open(pdf_path)
    page = pdf_document[0]
    image = page.get_pixmap(dpi=300)  # High-resolution image
    image.save(local_image_path)
    pdf_document.close()
    return local_image_path

def upload_image_to_gcs(local_image_path, bucket_name, destination_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(local_image_path)

@app.route("/")
def main():
    pdf_url = get_nyt_pdf_url()
    print(f"Downloading PDF from: {pdf_url}")
    
    try:
        pdf_path = download_pdf(pdf_url)
        print("PDF downloaded successfully.")
        
        # Define local path for storing the image
        local_image_path = "nyt_frontpage.png"
        
        # Convert PDF to image and store locally
        convert_pdf_to_image(pdf_path, local_image_path)
        
        # Upload image to Google Cloud Storage
        bucket_name = "doit-sascha-public"
        destination_blob_name = "news.png"
        upload_image_to_gcs(local_image_path, bucket_name, destination_blob_name)
        
        return "Image uploaded to Cloud Storage successfully.", 200
    except Exception as e:
        return f"An error occurred: {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
