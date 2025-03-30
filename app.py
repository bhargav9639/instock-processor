from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Instock Processor API is running!"})

@app.route("/process", methods=["POST"])
def process_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        # Read the file (assuming it's a CSV or Excel)
        if file.filename.endswith(".csv"):
            df = pd.read_csv(filepath)
        elif file.filename.endswith((".xls", ".xlsx")):
            df = pd.read_excel(filepath)
        else:
            return jsonify({"error": "Unsupported file type"}), 400

        # 🛠️ Process the Data (Modify as needed)
        df["Processed"] = "Yes"

        # Save the processed file
        output_filepath = os.path.join(UPLOAD_FOLDER, f"processed_{file.filename}")
        df.to_csv(output_filepath, index=False)

        return jsonify({"message": "File processed successfully!", "processed_file": output_filepath})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
