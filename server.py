import json

import flask
import pickle
from flask import Flask, request, send_from_directory

filename_root = './cancan21-train-annot1' 
filename_suffix = '.json.p'
app = Flask(__name__)
with open(filename_root + filename_suffix, 'rb') as handle:
    doc_list = pickle.load(handle)

doc_id_str = 'newdoc id'
token_key_str = 'tokens'

doc_index = 0

@app.route("/")
def hello_world():
    return send_from_directory('client/public', 'index.html')

# Path for all the static files (compiled JS/CSS, etc.)
@app.route("/<path:path>")
def home(path):
    return send_from_directory('client/public', path)


@app.route('/get-init-doc')
def get_init_doc():
    global doc_index
    doc_index = 0
    return get_current_doc()

@app.route('/get-current-doc')
def get_current_doc():
    doc = doc_list[doc_index]
    return json.dumps(doc)

@app.route('/doc-list')
def get_doc_list():
    return json.dumps([d[doc_id_str] for d in doc_list])

@app.route('/get-doc-relative', methods=['POST'])
def get_doc_relative():
    json_data = request.get_json()
    try:
        delta = int(json_data['delta'])
    except:
        return json.dumps({'error': '%s not a number' % json_data['delta']})
    global doc_index
    doc_index = (doc_index + delta) % len(doc_list)
    if doc_index < 0: doc_index += len(doc_list)
    return get_current_doc()
    # print(delta)
    # return json.dumps({'received':delta})

@app.route('/update-doc', methods=['POST'])
def update_doc():
    try:
        json_data = request.get_json()
        doc_id = json_data[doc_id_str]
        token_data = json_data[token_key_str]
    except:
        return json.dumps({'error': 'invalid data'})
    doc = [d for d in doc_list if d[doc_id_str] == doc_id]
    if len(doc) != 1:
        return json.dumps({'error':'number of docs %s found is %d' % (doc_id, len(doc))})
    doc = doc[0]
    for new, old in zip(token_data, doc[token_key_str]):
        old.update(new)
    return json.dumps({'response':'ok'})

import datetime

@app.route('/save-to-server')
def save_to_server():
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = filename_root + '-' + timestamp + filename_suffix
    with open(filename, 'wb') as handle:
        pickle.dump(doc_list, handle)
    return json.dumps({'response':'ok', 'filename':filename})

import os
@app.route('/get-file-list', )
def get_file_list():
    file_list = [f for f in os.listdir() if f.endswith('.json.p')]
    return json.dumps(file_list)

@app.route('/load-file', methods=['POST'])
def load_file():
    try:
        json_data = request.get_json()
        filename = json_data['filename']
    except Exception as e:
        return json.dumps({'error': 'invalid data: + %s' % str(e)})
    try:
        fptr = open(filename, 'rb')
    except Exception as e:
        return json.dumps({'error': 'file load error: + %s' % str(e)})
    _doc_list = pickle.load(fptr)
    # check if file ok
    file_ok = False
    if isinstance(_doc_list, list):
        file_ok = True
        for doc in _doc_list:
            if not (isinstance(doc, dict) and token_key_str in doc and doc_id_str in doc and
                    isinstance(doc[token_key_str], list) and isinstance(doc[doc_id_str], str)):
                file_ok = False
    if not file_ok:
        return json.dumps({'error':'Bad file format'})
    global doc_list, doc_index
    doc_list = _doc_list
    doc_index = 0
    return json.dumps({'response':'ok'})
    
if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000)
