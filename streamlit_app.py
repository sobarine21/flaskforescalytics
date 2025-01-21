import streamlit as st
from flask import Flask, request, jsonify
import threading
import google.generativeai as genai
import json
from werkzeug.serving import make_server

# Initialize Flask app
app = Flask(__name__)

# Configure Google Generative AI
genai.configure(api_key="YOUR_GOOGLE_API_KEY")

# Function to generate AI response based on the email content
def get_ai_response(prompt, email_content):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt + email_content[:1000])  # Limit email content to 1000 characters
        return response.text.strip()
    except Exception as e:
        return str(e)

# Endpoint for receiving email content from Zapier
@app.route('/process_email', methods=['POST'])
def process_email():
    data = request.json  # Get JSON data from the incoming request
    
    # Extract the email content
    email_content = data.get('email_content', '')
    
    # Check if email content is provided
    if not email_content:
        return jsonify({"error": "No email content provided"}), 400
    
    # Generate AI summary and response
    summary = get_ai_response("Summarize the email in a concise, actionable format:\n\n", email_content)
    response = get_ai_response("Draft a professional response to this email:\n\n", email_content)
    
    # Return AI-generated summary and response
    return jsonify({
        "summary": summary,
        "response": response
    })

# Function to start Flask API in a separate thread
def run_flask():
    server = make_server('0.0.0.0', 5000, app)
    server.serve_forever()

# Start Flask server in a separate thread
flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

# Streamlit UI code
st.title("Email Response Generator")
st.write("This tool processes incoming emails and generates a response using AI.")

email_content = st.text_area("Paste your email content here:")

if st.button("Generate Response"):
    if email_content:
        # Generate summary and response for the provided email content
        summary = get_ai_response("Summarize the email in a concise, actionable format:\n\n", email_content)
        response = get_ai_response("Draft a professional response to this email:\n\n", email_content)
        
        st.subheader("AI Summary")
        st.write(summary)
        
        st.subheader("Generated Response")
        st.write(response)
    else:
        st.warning("Please provide email content.")
