from flask import Flask, render_template, request, redirect, make_response
import requests
import json
import string
import random
import math
import os

app = Flask(__name__)

TWITTER_API = os.environ.get('TTKEY')
TWITTER_API_secret = os.environ.get('TTSECRET')
BEARER_TOKEN = os.environ.get('BTOKEN')

def randomStringDigits(stringLength=2):

    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))


def get_username_info(user):

    url = "https://api.twitter.com/2/users/by/username/{}?user.fields=profile_image_url".format(user)

    payload = {}
    headers = {
      'Authorization': 'Bearer {}'.format(BEARER_TOKEN),
      'Cookie': 'personalization_id="v1_p5/6aoRuy20KVDY7I31lDg=="; guest_id=v1%3A160359179220272467'
    }

    response = requests.request("GET", url, headers=headers, data = payload).json()
    print(response)
    return response

#Given user handle OR id! -> returns up to 50 tweets
def query_user_tweets(user):

    url = "https://api.twitter.com/2/tweets/search/recent?query=from:{}&max_results=50&tweet.fields=created_at".format(user)

    payload = {}
    headers = {
      'Authorization': 'Bearer {}'.format(BEARER_TOKEN),
      'Cookie': 'personalization_id="v1_p5/6aoRuy20KVDY7I31lDg=="; guest_id=v1%3A160359179220272467'
    }

    response = requests.request("GET", url, headers=headers, data = payload).json()

    return response


def get_user_friends(user):
    url = "https://api.twitter.com/1.1/friends/ids.json?screen_name={}".format(user)

    payload = {}
    headers = {
      'Authorization': 'Bearer {}'.format(BEARER_TOKEN),
      'Cookie': 'personalization_id="v1_p5/6aoRuy20KVDY7I31lDg=="; guest_id=v1%3A160359179220272467'
    }

    response = requests.request("GET", url, headers=headers, data = payload).json()

    return response


@app.route('/')
def root():
    return render_template('index.html')

@app.route('/results')
def show_results():
    return render_template('results.html')

@app.route('/eval', methods = ['POST'])
def evaluate():
    twtt_handle = request.form.get('handle')
    return json.dumps({'price':-1})


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [START gae_python37_render_template]
