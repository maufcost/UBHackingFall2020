from flask import Flask, render_template, request, redirect, make_response
import requests
import json
import string
import random
import math

app = Flask(__name__)

def randomStringDigits(stringLength=2):

    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))

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
