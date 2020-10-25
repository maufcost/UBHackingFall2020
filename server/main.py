from flask import Flask, render_template, request, redirect, make_response
import requests
import json
import string
import random
import math
import os
import re
import time

app = Flask(__name__)

TWITTER_API = os.environ.get('TTKEY')
TWITTER_API_secret = os.environ.get('TTSECRET')
BEARER_TOKEN = os.environ.get('BTOKEN')
AZURE_KEY = os.environ.get('AZURE_KEY')
ENDPOINT = "https://hellofriend.cognitiveservices.azure.com/"


def analyze_sentiment(text):
    sentiment_url = ENDPOINT + "/text/analytics/v3.0/sentiment"

    documents = {"documents": [
        {"id": "1", "language": "en",
        "text": "{}".format(text)}
        ]}

    headers = {"Ocp-Apim-Subscription-Key": AZURE_KEY}

    response = requests.post(sentiment_url, headers=headers, json=documents)
    sentiments = response.json()
    print(sentiments)
    time.sleep(0.6)
    return sentiments

def get_key_phrases(text):
    keyphrase_url = ENDPOINT + "/text/analytics/v3.0/keyphrases"

    documents = {"documents": [
        {"id": "1", "language": "en",
        "text": "{}".format(text)}
        ]}

    headers = {"Ocp-Apim-Subscription-Key": AZURE_KEY}

    response = requests.post(keyphrase_url, headers=headers, json=documents)

    key_phrases  = response.json()
    print(key_phrases)

    return key_phrases

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

    url = "https://api.twitter.com/2/tweets/search/recent?query=from:{} -is:retweet&max_results=20&tweet.fields=created_at".format(user)

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

def get_list_of_friends(user):
    url = "https://api.twitter.com/1.1/friends/list.json?screen_name={}&count=20".format(user)

    payload = {}
    headers = {
      'Authorization': 'Bearer {}'.format(BEARER_TOKEN),
      'Cookie': 'personalization_id="v1_p5/6aoRuy20KVDY7I31lDg=="; guest_id=v1%3A160359179220272467'
    }

    response = requests.request("GET", url, headers=headers, data = payload).json()
    return response

def process_sentiment(sentiment_obj):
    the_document = sentiment_obj.get("documents")[0]
    return [the_document.get('sentiment'), the_document.get('confidenceScores').get("positive"), the_document.get('confidenceScores').get("neutral"), the_document.get('confidenceScores').get("negative")]


def evaluate_tweets(recent_tweets_obj):
    if recent_tweets_obj.get("data"):
        results = []
        pos = 0
        neu = 0
        neg = 0
        current_points = [0,0,0]
        count = 0
        for each_tweet in recent_tweets_obj.get("data"):
            if each_tweet.get("text"):
                temp_obj = {}
                raw = each_tweet.get("text")
                only_text = re.sub(r"http\S+", "", raw)
                if len(only_text) < 10:
                    continue
                else:
                    print(only_text)
                    sentiment_obj = analyze_sentiment(only_text)

                    processed_results = process_sentiment(sentiment_obj) #['positive', pos%, neu%, neg%]

                    if processed_results[0] == 'positive':
                        pos += 1
                    elif processed_results[0] == 'negative':
                        neg += 1
                    elif processed_results[0] == 'neutral':
                        neu += 1
                    current_points[0] += processed_results[1]
                    current_points[1] += processed_results[2]
                    current_points[2] += processed_results[3]
                    count += 1
                    print(processed_results)
                    temp_obj['text'] = only_text
                    temp_obj['date'] = each_tweet.get("created_at")
                    temp_obj['res'] = processed_results
                    temp_obj['score'] = round((processed_results[1] * 1 + processed_results[2] * 0 + processed_results[3] * -1) * 100, 2)
                    results.append(temp_obj)
                    # key_phrase_obj = get_key_phrases(only_text)
        return [[pos,neu,neg, current_points, count], results]
    else:
        return []

def generate_user_object(network):
    processed_network = []

    analys = [0,0,0]
    overall_network_positivity = [0,0,0]
    c = 0

    for each_user in network.get("users"):
        temp_dict = {}
        temp_dict['name'] = each_user.get("name")
        temp_dict['id'] = each_user.get("id")
        temp_dict['handle'] = each_user.get("screen_name")
        temp_dict['url'] = each_user.get("url")
        temp_dict['img'] = each_user.get("profile_image_url_https")

        all_user_tweets = query_user_tweets(temp_dict['handle'])
        tweet_data = evaluate_tweets(all_user_tweets)#[1] Full crazy result -> [[pos,neu,neg, current_points, count], results]

        if len(tweet_data) == 0:
            continue
        analys[0] += tweet_data[0][0]
        analys[1] += tweet_data[0][1]
        analys[2] += tweet_data[0][2]

        overall_network_positivity[0] += tweet_data[0][3][0]
        overall_network_positivity[1] += tweet_data[0][3][1]
        overall_network_positivity[2] += tweet_data[0][3][2]
        c += tweet_data[0][4]


        temp_dict['tweet_data'] = tweet_data
        processed_network.append(temp_dict)

    return [processed_network, [analys ,overall_network_positivity, c]]


@app.route('/')
def root():
    #analyze_sentiment("I")
    return render_template('index.html')

@app.route('/eval', methods = ['POST'])
def evaluate():
    handle = request.form.get('user')

    basic_u_info = get_username_info(handle)

    recent_user_tweets = query_user_tweets(handle)
    user_individual_analysis = evaluate_tweets(recent_user_tweets) #[[pos,neu,neg, current_points -> [p, neu, neg], count], results]

    overall_user_score = round((user_individual_analysis[0][3][0]/user_individual_analysis[0][4] + (-1 * user_individual_analysis[0][3][2]/user_individual_analysis[0][4])) * 100, 2)

    users_network = get_list_of_friends(handle)
    temp = generate_user_object(users_network)
    network_full_analysis = temp[0]

    overall_net_score = round((temp[1][1][0]/temp[1][2] + (temp[1][1][2]/temp[1][2] * -1)) * 100, 2)

    pos = user_individual_analysis[0][0] + temp[1][0][0]
    neu = user_individual_analysis[0][1] + temp[1][0][1]
    neg = user_individual_analysis[0][2] + temp[1][0][2]

    return render_template('results.html', user=basic_u_info, user_a=user_individual_analysis, user_score = overall_user_score, full_net=network_full_analysis, net_score = overall_net_score, pos=pos, neg=neg, neu=neu)


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
