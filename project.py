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
    designation = data.get('recipient_designation', 'Professional')
    subject = data.get('subject', 'Email Subject')
    purpose = data.get('purpose', 'No purpose provided')
    tone = data.get('tone', 'Formal')
    key_content_points = data.get('key_content_points', 'Relevant details included')
    cta = data.get('cta', 'No CTA specified')
    sender_name = data.get('sender_name', 'Sender')
    closing = data.get('closing', 'Best regards,')

    # Construct prompt - now includes subject
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
        # Call Llama 4 Maverick model
        response = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=[
                {
                    "role": "system",
                    "content": (
                        """You are a professional email writer. Always respond with the final formatted email only.
Do not include any descriptions, prefaces, or explanations.
Format the email with a proper subject line, greeting, structured body, clear CTA, and signature."""
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


if __name__ == '__main__':
    app.run(debug=True)