# main.py
from flask import Flask, redirect, request, jsonify
import os, requests, urllib.parse

app = Flask(__name__)
CLIENT_ID = os.environ.get("ETSY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("ETSY_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("ETSY_REDIRECT_URI")
SCOPE = "listing_r shops_r"

@app.route("/")
def index():
    return ("<h3>Etsy OAuth Test</h3><p><a href='/oauth/connect'>Connect with Etsy</a></p>")

@app.route("/oauth/connect")
def oauth_connect():
    if not CLIENT_ID or not REDIRECT_URI:
        return "ETSY_CLIENT_ID or ETSY_REDIRECT_URI not set in env", 500
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "state": "xyz123"
    }
    auth_url = "https://www.etsy.com/oauth/connect?" + urllib.parse.urlencode(params)
    return redirect(auth_url)

@app.route("/oauth/callback")
def oauth_callback():
    code = request.args.get("code")
    error = request.args.get("error")
    if error:
        return f"OAuth error: {error}", 400
    if not code:
        return "Missing code in callback", 400

    token_url = "https://api.etsy.com/v3/public/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(token_url, data=data, headers=headers, timeout=20)
    try:
        j = resp.json()
    except Exception:
        return f"Token response not JSON: status {resp.status_code} body: {resp.text}", 500
    return jsonify({"status_code": resp.status_code, "token_response": j})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
