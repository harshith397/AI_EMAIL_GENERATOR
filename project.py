from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv
from flask_cors import CORS
from groq import Groq

# Load environment variables from .env
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# Enable CORS for all routes
CORS(app)

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Home route serving HTML page
@app.route('/')
def index():
    return render_template('home.html')  # Make sure home.html exists in templates/

# API route to generate email
@app.route('/generate_email', methods=['POST'])
def generate_email():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request. Expected JSON data"}), 400

    # Extract form data
    recipient_name = data.get('recipient_name', 'Recipient')
    designation = data.get('recipient_designation', 'Professional')
    subject = data.get('subject', 'Email Subject')
    purpose = data.get('purpose', 'No purpose provided')
    tone = data.get('tone', 'Formal')
    key_content_points = data.get('key_content_points', 'Relevant details included')
    cta = data.get('cta', 'No CTA specified')
    sender_name = data.get('sender_name', 'Sender')
    closing = data.get('closing', 'Best regards,')

    # Prompt for LLM
    prompt = f"""
    Write a formal email to {recipient_name}, who is a {designation}.

Subject: {subject}
Purpose: {purpose}
Key Points:
{key_content_points}
Call to Action: {cta}
Closing: {closing}
Sender: {sender_name}

Only generate the final email without any introductory statements or formatting notes.
    """

    try:
        # Llama 4 API call
        response = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert email writer tasked with crafting professional, concise, and effective emails based on user-provided inputs from an AI Email Generator form. Respond exclusively with the final formatted email, adhering to the following guidelines:\n"
                        "- Use the provided `recipient_name` and `recipient_designation` (if available) to personalize the greeting. If `recipient_designation` is empty, omit it but maintain professionalism.\n"
                        "- Set the subject line exactly as provided in `email_subject`.\n"
                        "- Structure the body to clearly address the `email_purpose`, keeping paragraphs concise and relevant to the user's intent.\n"
                        "- Incorporate the `call_to_action` as a specific, actionable CTA if provided; otherwise, include a natural closing statement.\n"
                        "- Use the `sender_name` in the signature, adding a professional title or contact information only if explicitly provided.\n"
                        "- Apply the selected `email_tone` (Formal, Semi-formal, or Casual) to dictate the language and style.\n"
                        "- Use the selected `email_closing` (e.g., Best regards, Sincerely, Thanks, Warm regards) for the signature.\n"
                        "- Do not include any explanations, prefaces, or additional commentary outside the formatted email.\n"
                        "- Ensure the email is complete and aligned"
                    )
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=512,
            temperature=0.7
        )

        email_text = response.choices[0].message.content
        return jsonify({"generated_email": email_text})

    except Exception as e:
        return jsonify({"error": f"Failed to generate email: {str(e)}"}), 500

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
