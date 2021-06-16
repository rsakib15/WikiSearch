from flask import request
from flask import Flask
# from flask import jsonify
from benchmark.speed import score_main
from search_engine.fuzzy_search import FuzzySearch
from search_engine.search import *
from suggestion.query_suggestion import QuerySuggestion
from indexing.index_main import index_dataset, get_directory_file_list
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, support_credentials=True)

@app.route('/')
def index():
    return "Server is running"

@app.route('/search', methods=['GET'])
def search():
    print("Search Called")
    print(request.args.get('q'))
    print(request.args.get('m'))
    res = searcher(request.args.get('q'), request.args.get('m'))
    print(res)
    return res

@app.route('/score',methods=['GET'])
def score():
    score_main()
    return {}

@app.route('/suggestion', methods=['GET'])
def suggestion():
    search_term = request.args.get('q')
    wikis = get_directory_file_list("dataset/extracted_dataset/text/")
    fuzzy = FuzzySearch(wikis)
    start = time.time()
    fuzzy.load()
    finish = time.time()
    output = fuzzy.process_fuzzy(search_term)
    return {"result": output[1]}


@app.route('/index', methods=['GET'])
def indexing():
    index_dataset()
    return {"status": "Indexing Completed"}


if __name__ == '__main__':
    index = False
    if index:
        indexing()
    app.run(host="127.0.0.1", port=5000, debug=True)
