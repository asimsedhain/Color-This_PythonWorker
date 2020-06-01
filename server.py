from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/", methods = ["POST", "GET"])
def bas():
	return jsonify(testing="Testing")

if __name__ == "__main__":
	
	app.run(port=80, host='0.0.0.0')
