import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from TeraboxDL import TeraboxDL

app = Flask(__name__)
CORS(app) 

@app.route('/')
def index():
    return jsonify({"status": "success", "message": "Terabox API is running using TeraboxDL."})

@app.route('/api/terabox', methods=['GET'])
def extract_terabox():
    share_url = request.args.get("url", "").strip()

    if not share_url:
        return jsonify({"status": "error", "message": "Missing 'url' parameter"}), 400

    ndus_cookie = os.environ.get("NDUS_COOKIE")
    if not ndus_cookie:
        return jsonify({"status": "error", "message": "NDUS_COOKIE is not set in Render."}), 500

    formatted_cookie = f"lang=en; ndus={ndus_cookie};"

    try:
        # FORCE the URL to use the main terabox domain for the library
        surl = share_url.split('/s/')[-1].strip()
        official_share_url = f"https://www.terabox.com/s/{surl}"

        # Initialize the bypasser
        terabox = TeraboxDL(formatted_cookie)
        
        # Pass the OFFICIAL url to the library, not the terasharefile one
        file_info = terabox.get_file_info(official_share_url)

        if "error" in file_info:
            return jsonify({"status": "error", "message": file_info["error"]}), 400

        return jsonify({
            "status": "success",
            "files": [{
                "filename": file_info.get("file_name"),
                "size": file_info.get("file_size"),
                "download_link": file_info.get("download_link"),
                "thumbnail": file_info.get("thumbnail")
            }]
        })

    except Exception as e:
        return jsonify({"status": "error", "message": f"Server Error: {str(e)}"}), 500
        

    try:
        # Initialize the bypasser
        terabox = TeraboxDL(formatted_cookie)
        
        # Fetch the file info automatically
        file_info = terabox.get_file_info(share_url)

        # The library returns an "error" key if the link is dead or cookie is invalid
        if "error" in file_info:
            return jsonify({
                "status": "error", 
                "message": file_info["error"]
            }), 400

        # Success! Return the data formatted for your frontend player
        return jsonify({
            "status": "success",
            "files": [{
                "filename": file_info.get("file_name"),
                "size": file_info.get("file_size"),
                "download_link": file_info.get("download_link"),
                "thumbnail": file_info.get("thumbnail")
            }]
        })

    except Exception as e:
        return jsonify({"status": "error", "message": f"Server Error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
