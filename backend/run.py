from flask import request
from flask import Flask,  render_template

app = Flask(__name__)

@app.route('/')
def index():
    return "Server is running"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False)