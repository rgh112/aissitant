# Import the Flask class from the flask module
from flask import Flask, render_template, request, jsonify

import openai
from flask_cors import CORS
from dotenv import load_dotenv
import os
from googleapiclient.discovery import build


load_dotenv("./.env")

app = Flask(__name__)
CORS(app, resources={r"/ask": {"origins": "*"}})

# Initialize the Google Search API client
def google_search(search_query, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_query, cx=cse_id, **kwargs).execute()
    return res['items']

# Set the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Handle requests to the home page
@app.route("/")
def home():
    return render_template("home-.html")

@app.route("/fixed.html")
def index():
    return render_template("fixed.html")

@app.route("/fixedfake.html")
def fake():
    return render_template("fixedfake.html")

@app.route("/ask", methods=["POST"])
def ask():
    try:
        # Get the question from the POST request
        question = request.form["question"]
        print(f"Received question: {question}")

        # Your Google API Key and CSE ID
        my_api_key = os.getenv("GOOGLE_API_KEY")
        my_cse_id = os.getenv("CSE_ID")

        # If the question is a Google Search
        if question.startswith("Google Search: "):
            search_query = question[len("Google Search: "):]
            # Google Search API 호출
            search_results = google_search(search_query, my_api_key, my_cse_id, num=5)
            search_results_str = "\n".join([result["title"] for result in search_results])
            return jsonify({"answer": search_results_str})

        # Otherwise, handle as OpenAI API call
        else:
            question_translated = question  # Initialize to handle cases that are not translation
            
            if question.startswith('translate to '):
                prefix, text_to_translate = question.split(": ", 1)
                language = prefix.split(" ")[2]
                question_translated = f"Translate the following text to {language}: {text_to_translate}"
                print(f"Question to be sent to API: {question_translated}")

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": question_translated},
                ],
            )
            
            answer = response["choices"][0]["message"]["content"]
            return jsonify({"answer": answer})

    except Exception as e:
        print(f"An exception occurred: {e}")
        return jsonify({"error": str(e)})

print("API Key:", os.getenv("OPENAI_API_KEY"))


# Run the Flask app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)