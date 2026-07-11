import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

@app.route('/')
def index():
    return jsonify({"status": "success", "message": "Terabox API is running via Gateway Proxy."})

@app.route('/api/terabox', methods=['GET'])
def extract_terabox():
    share_url = request.args.get("url", "").strip()

    if not share_url:
        return jsonify({"status": "error", "message": "Missing 'url' parameter"}), 400

    try:
        # We proxy the request to an actively maintained open-source extraction gateway
        # This prevents your API from breaking when Terabox updates their security
        gateway_api = "https://tera-core.vercel.app/api2"
        
        # Pass the user's URL to the gateway
        resp = requests.get(gateway_api, params={"url": share_url}, timeout=20)
        data = resp.json()

        # Handle the gateway's response
        raw_files = data.get("files") or ([data] if data.get("direct_link") else [])

        files = []
        for f in raw_files:
            files.append({
                "filename": f.get("filename") or f.get("file_name"),
                "size": f.get("size"),
                "thumbnail": f.get("thumbnail") or f.get("thumb"),
                "download_link": f.get("direct_link") or f.get("download_link"),
                "stream_link": f.get("stream_link"),
            })

        if not files or not files[0].get("download_link"):
            return jsonify({
                "status": "error",
                "message": data.get("message") or "No playable files found. The link might be dead."
            }), 404

        return jsonify({"status": "success", "files": files})

    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"Gateway Extraction failed: {str(e)}"
        }), 502

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
