import json
import time
from flask import Flask, request, render_template, redirect, flash, make_response
import requests
import os
from flask import Flask, request, redirect, url_for
from google.oauth2 import credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.secret_key = "abc"
# This is important. Enables X-Forward-Proto to tell oauth2 that client-nginx traffic is ssl
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)

headers = {
    "accept": "application/json",
    "content-type": "application/json"
}


# YouTube API credentials
CLIENT_SECRETS_FILE = 'client_secrets.json'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


def download_video(url):
    try:
        response = requests.get(url)
        video_filename = "video.mp4"
        with open(video_filename, 'wb') as file:
            file.write(response.content)
        print("Download complete")
        return video_filename
    except Exception as e:
        print(f"Error downloading video from HTTP server: {e}")
        return None

# Function to get the authorization URL
def get_authorization_url():
    #flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    #flow.redirect_uri = request.base_url + '/callback'
    #authorization_url, _ = flow.authorization_url(access_type='offline', prompt='consent')
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    # Use 'https' instead of 'http' in the redirect URL
    flow.redirect_uri = url_for('handle_authorization_callback', _external=True, _scheme='https')
    authorization_url, _ = flow.authorization_url(access_type='offline', prompt='consent')
    return authorization_url

# Function to handle the authorization callback
@app.route('/authorize/callback')
def handle_authorization_callback():
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    #flow.redirect_uri = request.base_url
    flow.redirect_uri = url_for('handle_authorization_callback', _external=True, _scheme='https')
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials

    # Save the credentials to a file or database for future usage
    # For simplicity, we'll just store it in a global variable
    global youtube_credentials
    youtube_credentials = credentials

    return redirect(url_for('my_form'))   # another option is to resume upload by calling my_form_upload, but you need to pass vidUrl somehow

# Function to upload video to YouTube
def upload_video(youtube, video_path, title, description, tags=None, category_id='22'):
    # Create video resource
    media = MediaFileUpload(download_video(video_path))

    # Set video metadata
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags or [],
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': 'private'
        }
    }

    # Upload video
    request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)
    response = request.execute()

    return response

def is_rendering(vId):
    try:
        url = " https://apis.elai.io/api/v1/videos/" + vId
        bearer = request.cookies.get('bearer')
        headers['Authorization'] = bearer
        response = requests.get(url, headers=headers)
	#mojlib.prettyprint(response.text)
        status = response.json()["status"]
        if status == "rendering":
            return True
        else:
            return False
    except:
        return False




@app.route('/')
def my_form():


    # Get the value of a cookie named 'bearer'
    bearer = request.cookies.get('bearer')

    # Check if the cookie exists and is not None
    if bearer is not None:
        
        url = " https://apis.elai.io/api/v1/videos/"
        headers['Authorization'] = bearer
        response = requests.get(url, headers=headers)
        #mojlib.prettyprint(response.text)
        #status = response.json()["status"]
        videos = []
        for element in response.json()["videos"]:
            url = "-"
            if element["status"] == "ready":
                url = element["url"]
            videos.append({"status": element["status"], "id": element["_id"], "url": url})

        return render_template('form.html', videos = videos)
    else:
        return render_template('bearer_input.html')

@app.route('/save_bearer', methods=['POST'])
def my_form_save_bearer():
    bearer = request.form['bearer']
    if bearer:
        response = make_response(redirect('/'))  # Create a redirect response
        response.set_cookie('bearer', "Bearer " + bearer, max_age=2592000) #1 month
        return response
    else:
        return 'Error: Bearer field is missing in the POST request.'


@app.route('/', methods=['POST'])
def my_form_post():
    bearer = request.cookies.get('bearer')
    title = request.form['title']
    text = request.form['text']
    #expireUTC = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(expireUTCsec))

    url = "https://apis.elai.io/api/v1/videos"

    payload = {
     "id": "3",
     "data": {
        "format": "9_16",
        "resolution": "FullHD"
     },
     "name": "Moj testni video 7",
     "slides": [
        {
            "animation": "fade_in",
            "avatar": {
                "canvas": "https://elai-media.s3.eu-west-2.amazonaws.com/cartoons/elai/regular/regular.png",
                "gender": "male",
                "id": "elai-cartoon.elai_regular_anim",
                "name": "Standing",
                "status": 2,
                "thumbnail": "https://elai-media.s3.eu-west-2.amazonaws.com/cartoons/elai/regular/regular.png",
                "type": "cartoon",
                "version": 1
            },
            "canvas": {
              "objects": [
                {
                  "id": 1,
                  "scaleX":	0.11,
                  "scaleY":	0.35,
                  "type": "image",
                  "left": 217,
                  "top": 0,
                  "src": "https://elai-media.s3.eu-west-2.amazonaws.com/backgrounds/abstract1.jpg?withcors",
                  "height":	1080,
                  "width":	1920,
                  "visible": True,
                  "version": 4,
                  "globalCompositeOperation":	"source-over"
                },
                {
                  "angle": 0,
                  "backgroundColor": "",
                  "charSpacing": 0,
                  "fill": "#000000",
                  "fillRule": "nonzero",
                  "flipX": False,
                  "flipY": False,
                  "fontFamily": "Galada",
                  "fontSize": 31,
                  "fontStyle": "normal",
                  "fontWeight": "normal",
                  "globalCompositeOperation": "source-over",
                  "height": 35.03,
                  "id": 823209052152,
                  "left": 226.34,
                  "lineHeight": 1.16,
                  "linethrough": False,
                  "opacity": 1,
                  "originX": "left",
                  "originY": "top",
                  "overline": False,
                  "paintFirst": "fill",
                  "scaleX": 1,
                  "scaleY": 1,
                  "skewX": 0,
                  "skewY": 0,
                  "strokeDashOffset": 0,
                  "strokeLineCap": "butt",
                  "strokeLineJoin": "miter",
                  "strokeMiterLimit": 4,
                  "strokeUniform": False,
                  "strokeWidth": 1,
                  "text": title,
                  "textAlign": "left",
                  "textBackgroundColor": "",
                  "top": 19.07,
                  "type": "i-text",
                  "underline": False,
                  "version": "4.4.0",
                  "visible": True,
                  "width": 183.8
                },
                {
                        "angle": 0,
                        "avatarType": "transparent",
                        "backgroundColor": "",
                        "cropX": 0,
                        "cropY": 0,
                        "fill": "#a56ced",
                        "fillRule": "nonzero",
                        "filters": [],
                        "flipX": False,
                        "flipY": False,
                        "globalCompositeOperation": "source-over",
                        "height": 0,
                        "left": 199,
                        "opacity": 1,
                        "originX": "left",
                        "originY": "top",
                        "paintFirst": "fill",
                        "scaleX": 0.24,
                        "scaleY": 0.24,
                        "skewX": 0,
                        "skewY": 0,
                        "src": "https://elai-media.s3.eu-west-2.amazonaws.com/cartoons/elai/regular/regular.png",
                        "strokeDashOffset": 0,
                        "strokeLineCap": "butt",
                        "strokeLineJoin": "miter",
                        "strokeMiterLimit": 4,
                        "strokeUniform": False,
                        "strokeWidth": 0,
                        "top": 95.44,
                        "type": "avatar",
                        "version": 1,
                        "visible": True,
                        "width": 0
                }
              ],
              "background": "#ffffff",
              "version": "4.4.0"
            },
            "hasAvatar": True,
            "id": 1,
            "language": "English",
            "speech": text,
            "voice": "en-IE-ConnorNeural",
            "voiceProvider": "azure",
            "voiceType": "text"
        }
     ]
    }

    print(type(payload))
    print(type(headers))
    print(payload)
    print(headers)
    headers['Authorization'] = bearer
    response = requests.post(url, json=payload, headers=headers)
    print(response.text)
    videoId = response.json()["_id"]
    print(videoId)
    #mojlib.prettyprint(response.text)

    url = "https://apis.elai.io/api/v1/videos/render/" + videoId
    response = requests.post(url, headers=headers)
    print(response.text)

    flash(response.text, 'OK')
    return redirect(request.referrer)


@app.route('/delete', methods=['GET'])
def my_form_delete():
    vidId = request.args.get('vidId')
    url = "https://apis.elai.io/api/v1/videos/" + vidId
    bearer = request.cookies.get('bearer')
    headers['Authorization'] = bearer
    response = requests.delete(url, headers=headers)
    #print(response.text)
    flash("Deleted", 'OK')
    return redirect(request.referrer)

    #return 'Data with ID {} deleted.'.format(vidId)


@app.route('/upload', methods=['GET'])
def my_form_upload():
    vidUrl = request.args.get('vidUrl')
    if 'youtube_credentials' not in globals() or not youtube_credentials.valid:
        authorization_url = get_authorization_url()
        return redirect(authorization_url)
    print("Downloading: ")
    print(vidUrl)
    youtube = build('youtube', 'v3', credentials=youtube_credentials)
    resp = upload_video(youtube,vidUrl,"Title","Description",[],"22")
    #resp = upload_video(vidUrl)
    #print(resp.text)
    video_id = resp['id']
    return f"Video uploaded successfully! Video ID: {video_id}"
    #flash(resp, 'OK')
    #return redirect(request.referrer)


if __name__ == "__main__":
    if 'videoId' not in globals():
        videoId = "x"
    app.run()



