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
        topic = data.get("topic")

        # ✅ FIX: Check empty input
        if not topic or topic.strip() == "":
            return jsonify({"error": "Topic is required"}), 400

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a professional documentation writer."},
                {"role": "user", "content": f"Generate documentation about {topic}"}
            ]
        )

        return jsonify({
            "result": response.choices[0].message.content
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ Important for React routing
@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, path)


if __name__ == "__main__":
    app.run(debug=True)