from flask import Flask, request, send_file
import pandas as pd
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/process', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return {"error": "No file provided"}, 400

    file = request.files['file']
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Process the file using the logic from 1500.py
    output_filename = process_stock_data(file_path)

    return send_file(output_filename, as_attachment=True)

def process_stock_data(file_path):
    """Process stock data similar to 1500.py."""
    df = pd.read_excel(file_path)  # Modify for CSV if needed
    df["Processed"] = "Yes"  # Dummy processing, replace with real logic

    output_file = os.path.join(OUTPUT_FOLDER, "processed_" + os.path.basename(file_path))
    df.to_excel(output_file, index=False)
    return output_file

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
