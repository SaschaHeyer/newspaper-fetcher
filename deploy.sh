gcloud run deploy nyt-pdf-to-image \
  --image gcr.io/YOUR_PROJECT_ID/nyt-pdf-to-image \
  --platform managed \
  --region YOUR_REGION \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
