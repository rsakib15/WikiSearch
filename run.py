from flask import request
from flask import Flask,  render_template
from flask_cors import CORS
from flask import jsonify
from search_engine.fuzzy_search import *
from suggestion.query_suggestion import QuerySuggestion
from indexing.index_main import index_dataset
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "Server is running"

@app.route('/search', methods=['GET'])
def search():
    print("Search Called")
    res = fuzzy_search(request.args.get('q'),request.args.get('m'))
    return res

@app.route('/page',methods=['GET'])
def page():
    print("Page")

@app.route('/suggestion', methods=['GET'])
def suggestion():
    print("Suggestion")
    query = request.args.get('search')
    suggestion_obj = QuerySuggestion(5)
    res = suggestion_obj.suggest(partial_query=query)
    #res = [{'value': item} for item in res]
    return {}

def indexing():
    index_dataset()

if __name__ == '__main__':
    index = False
    if index:
        indexing()
    app.run(host="127.0.0.1", port=5000, debug=True)
