from flask import Flask, request, jsonify, send_file
import pandas as pd
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return jsonify({"message": "Instock Processor API is running!"})

@app.route('/process', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    allowed_extensions = ['.xlsx', '.csv']
    
    if file_ext not in allowed_extensions:
        return jsonify({"error": "Invalid file format. Only .xlsx and .csv allowed."}), 400
    
    # Ensure unique filenames to avoid overwriting
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(file_path)
    
    try:
        if file_ext == '.xlsx':
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)
        
        # Example Processing: Add a new column
        df['Processed'] = 'Yes'
        
        output_filename = f"processed_{unique_filename}"
        output_path = os.path.join(PROCESSED_FOLDER, output_filename)
        
        if file_ext == '.xlsx':
            df.to_excel(output_path, index=False)
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        else:
            df.to_csv(output_path, index=False)
            mimetype = 'text/csv'
        
        return send_file(output_path, as_attachment=True, mimetype=mimetype)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(file_path)  # Cleanup uploaded file after processing

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
