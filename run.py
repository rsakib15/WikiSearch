from flask import request
from flask import Flask
from flask_cors import CORS
# from flask import jsonify
from benchmark.speed import score_main
from search_engine.fuzzy_search import FuzzySearch
from search_engine.search import *
from suggestion.query_suggestion import QuerySuggestion
from indexing.index_main import index_dataset, get_directory_flie_list

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "Server is running"

@app.route('/search', methods=['GET'])
def search():
    print("Search Called")
    res = search(request.args.get('q'),request.args.get('m'))
    return res

@app.route('/score',methods=['GET'])
def score():
    score_main()
    return {}

@app.route('/suggestion', methods=['GET'])
def suggestion():
    # print("Suggestion")
    # query = request.args.get('search')
    # suggestion_obj = QuerySuggestion(5)
    # res = suggestion_obj.suggest(partial_query=query)
    # #res = [{'value': item} for item in res]
    # return {}

    wikis = get_directory_flie_list("dataset/extracted_dataset/text/")
    fuzzy = FuzzySearch(wikis)
    if fuzzy.exists():
        print("Generating Fuzzy Search")
        start = time.time()
        fuzzy.create()
        finish = time.time()
        print("Generated Fuzzy Search in {} seconds".format(str(finish - start)))
    else:
        print("Loading Fuzzy Search")
        start = time.time()
        fuzzy.load()
        finish = time.time()
        print("Loaded Fuzzy Search in {} seconds".format(str(finish - start)))
    print(fuzzy.process_fuzzy('Alex*r the graet'))


@app.route('/index', methods=['GET'])
def indexing():
    index_dataset()
    return {"status": "Indexing Completed"}


if __name__ == '__main__':
    index = False
    if index:
        indexing()
    app.run(host="127.0.0.1", port=5000, debug=True)
