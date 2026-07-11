import os
import re
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS so your frontend can communicate with this API
CORS(app) 

@app.route('/')
def index():
    return jsonify({
        "status": "success",
        "message": "Terabox API is running.",
        "usage": "/api/terabox?url=YOUR_TERABOX_LINK"
    })

@app.route('/api/terabox', methods=['GET'])
def extract_terabox():
    share_url = request.args.get("url", "").strip()

    if not share_url:
        return jsonify({"status": "error", "message": "Missing 'url' parameter"}), 400

    # Fetch the NDUS cookie from server environment variables for security
    ndus_cookie = os.environ.get("NDUS_COOKIE")
    if not ndus_cookie:
        return jsonify({
            "status": "error", 
            "message": "Server configuration error: NDUS_COOKIE is not set in environment variables."
        }), 500

    try:
        # 1. Extract the unique ID (surl) regardless of what domain the user pasted
        surl = share_url.split('/s/')[-1].strip()
        if not surl.startswith('1'):
            surl = '1' + surl

        # FORCE the URL to use the main terabox domain. 
        # This makes the API work for terasharefile, nephobox, 1024tera, etc.
        official_share_url = f"https://www.terabox.com/s/{surl}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Cookie": f"ndus={ndus_cookie};"
        }

        # 2. Fetch the share page from the official domain
        session = requests.Session()
        page_resp = session.get(official_share_url, headers=headers, timeout=15)
        
        match = re.search(r'window\.yunData\s*=\s*({.*?});', page_resp.text)
        if not match:
            return jsonify({
                "status": "error", 
                "message": "Could not extract tokens. The cookie might be expired or the link is invalid."
            }), 400
            
        yun_data = json.loads(match.group(1))
        
        # 3. Call Terabox's internal API to get the direct file list
        api_url = "https://www.terabox.com/share/list"
        params = {
            "app_id": "250528",
            "web": "1",
            "channel": "dubox",
            "jsToken": yun_data.get("jsToken"),
            "shorturl": surl,
            "root": "1",
            "sign": yun_data.get("sign"),
            "timestamp": yun_data.get("timestamp"),
            "shareid": yun_data.get("shareid"),
            "uk": yun_data.get("uk")
        }

        list_resp = session.get(api_url, params=params, headers=headers, timeout=15)
        data = list_resp.json()

        if data.get("errno") != 0:
            return jsonify({"status": "error", "message": f"Terabox API error: {data.get('errno')}"}), 400

        files = data.get("list", [])
        if not files:
            return jsonify({"status": "error", "message": "No files found in this link."}), 404

        # 4. Return the first file's direct link
        first_file = files[0]
        return jsonify({
            "status": "success",
            "files": [{
                "filename": first_file.get("server_filename"),
                "size": first_file.get("size"),
                "download_link": first_file.get("dlink"),
                "thumbnail": first_file.get("thumbs", {}).get("url3")
            }]
        })

    except Exception as e:
        return jsonify({"status": "error", "message": f"Extraction failed: {str(e)}"}), 500

if __name__ == '__main__':
    # Use PORT provided by the environment (Render/Heroku compatible)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
