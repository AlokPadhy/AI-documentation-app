from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from groq import Groq

app = Flask(__name__, static_folder="build", static_url_path="")
CORS(app)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ✅ Serve React frontend
@app.route("/")
def serve():
    return send_from_directory(app.static_folder, "index.html")

# ✅ API route
@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json()
        prompt = data.get("prompt")

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return jsonify({
            "content": response.choices[0].message.content
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


# ✅ Important for React routing
@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, path)


if __name__ == "__main__":
    app.run(debug=True)