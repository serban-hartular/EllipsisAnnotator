import json

import flask
import pickle
from flask import Flask, request, send_from_directory

app = Flask(__name__)
with open('./cancan21-train-annot1-json.p', 'rb') as handle:
    doc_list = pickle.load(handle)

@app.route("/")
def hello_world():
    return send_from_directory('client/public', 'index.html')

# Path for all the static files (compiled JS/CSS, etc.)
@app.route("/<path:path>")
def home(path):
    return send_from_directory('client/public', path)


@app.route('/form-example', methods=['GET', 'POST'])
def form_example():
    # handle the POST request
    if request.method == 'POST':
        language = request.form.get('language')
        framework = request.form.get('framework')
        return '''
                  <h1>The language value is: {}</h1>
                  <h1>The framework value is: {}</h1>'''.format(language, framework)


@app.route('/tok-data')
def get_tok_data():
    doc = [d for d in doc_list if d['newdoc id'] == 'cancan21-0153']
    doc = doc[0] if doc else []
    print(doc)
    return json.dumps(doc['tokens'])
    # return json.dumps([{'form':'Am', 'str_after': ' ', 'id':'0'},
    #                    {'form':'opșpe', 'str_after': ' ', 'id':'1'},
    #                    {'form': 'lei', 'str_after': '', 'id': '2'},
    #                    {'form': '.', 'str_after': '\n', 'id': '3'},
    #                    ])

@app.route('/json-example')
def json_example():
    request_data = request.get_json()
    return 'JSON Object Example'

if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000)
