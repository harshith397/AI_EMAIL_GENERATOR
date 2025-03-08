from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv
from groq import Groq


# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')  # Ensure "home.html" is inside the "templates" folder

@app.route('/generate_email', methods=['POST'])
def generate_email():
    data = request.get_json()  # Ensure we receive JSON data
    if not data:
        return jsonify({"error": "Invalid request. Expected JSON data"}), 400

    recipient_name = data.get('recipient_name', 'Recipient')
    designation = data.get('designation', 'Professional')
    purpose = data.get('purpose', 'No purpose provided')
    tone = data.get('tone', 'Formal')
    key_content_points = data.get('key_content_points', 'Relevant details included')
    cta = data.get('cta', 'No CTA specified')
    sender_name = data.get('sender_name', 'Sender')
    closing = data.get('closing', 'Best regards,')

    # Construct prompt
    prompt = f"""
    Write a {tone} email to {recipient_name}, who is a {designation}. 
    The purpose of the email is: {purpose}
    
    Key details to mention:
    {key_content_points}
    
    The email should include a clear Call to Action (CTA): {cta}.
    
    Conclude the email with: {closing}.
    
    The email is from: {sender_name}.
    """

    # Call Groq's Mixtral model
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {"role": "system", "content": "You are an expert email writer."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=512,
        temperature=0.7
    )

    email_text = response.choices[0].message.content

    return jsonify({"generated_email": email_text})

if __name__ == '__main__':
    app.run(debug=True)