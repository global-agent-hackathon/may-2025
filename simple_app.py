from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>Hello World!</h1>"

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"message": "API is working!"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 