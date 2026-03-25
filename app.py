from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="build", static_url_path="")
CORS(app)

# ✅ Load API key
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found")

client = Groq(api_key=api_key)


# ✅ API ROUTE
@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json()
        topic = data.get("topic")

        if not topic:
            return jsonify({"error": "Topic is required"}), 400

        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",  # ✅ working model
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional documentation writer. Use headings, bullet points, and structured format."
                },
                {
                    "role": "user",
                    "content": f"Generate detailed documentation about {topic}"
                }
            ]
        )

        content = response.choices[0].message.content

        return jsonify({"result": content})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500


# ✅ SERVE FRONTEND
@app.route("/")
def serve():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)


if __name__ == "__main__":
    app.run()