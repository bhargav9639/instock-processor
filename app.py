import os
import pandas as pd
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
CORS(app)  # Allow CORS for API requests

# Load the master SKU file
MASTER_SKU_FILE = "1500Skus.xlsx"
if not os.path.exists(MASTER_SKU_FILE):
    raise FileNotFoundError(f"{MASTER_SKU_FILE} not found. Upload it to the project directory.")

master_skus = pd.read_excel(MASTER_SKU_FILE)

# Email settings (Update with your credentials)
EMAIL_SENDER = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"  # Use App Password if using Gmail

@app.route('/upload', methods=['POST'])
def process_file():
    """Handles file upload, processes it, and sends output via email."""
    
    # 1️⃣ Get uploaded file and email
    if 'file' not in request.files or 'email' not in request.form:
        return jsonify({"error": "Missing file or email"}), 400

    uploaded_file = request.files['file']
    email = request.form['email']

    if uploaded_file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # 2️⃣ Read uploaded Excel file
    uploaded_data = pd.read_excel(uploaded_file)

    # 3️⃣ Compare SKUs (Assume column name is "SKU" in both files)
    matched_skus = uploaded_data[uploaded_data['SKU'].isin(master_skus['SKU'])]

    # 4️⃣ Save output file
    output_filename = "matched_skus.xlsx"
    matched_skus.to_excel(output_filename, index=False)

    # 5️⃣ Send email with processed file
    if send_email(email, output_filename):
        return jsonify({"message": "File processed & sent successfully!"}), 200
    else:
        return jsonify({"error": "Failed to send email"}), 500

def send_email(receiver_email, attachment_path):
    """Sends an email with the processed file."""
    try:
        msg = EmailMessage()
        msg['Subject'] = "Processed SKU File"
        msg['From'] = EMAIL_SENDER
        msg['To'] = receiver_email
        msg.set_content("Please find the processed SKU file attached.")

        # Attach file
        with open(attachment_path, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="xlsx", filename=attachment_path)

        # Send email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)

        return True
    except Exception as e:
        print(f"Email Error: {e}")
        return False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
