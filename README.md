# Terabox Extraction API

This is a Python Flask backend designed to extract direct download and streaming links from Terabox share URLs.

## How to Deploy to Render (Free Cloud Hosting)

1. Upload all of these files to a new repository on your GitHub account.
2. Go to [Render.com](https://render.com) and log in.
3. Click **New +** and select **Web Service**.
4. Connect your GitHub account and select your repository.
5. In the settings, set the following:
   - **Environment:** Python 3
   - **Start Command:** `gunicorn app:app`
6. Scroll down to **Environment Variables** and add a new one:
   - **Key:** `NDUS_COOKIE`
   - **Value:** *(Paste your Terabox ndus cookie here)*
7. Click **Deploy Web Service**.

Once deployed, you can extract links by visiting:
`https://your-app.onrender.com/api/terabox?url=YOUR_TERABOX_LINK`
