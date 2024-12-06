from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)

def detect_anomalies(df, metric_column):
    threshold = np.percentile(df[metric_column], 95)  # 95-й перцентиль
    df['anomaly_flag'] = df[metric_column] > threshold
    return df

CORS(app)

@app.route('/anomalies', methods=['POST'])
def anomalies():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    print('file', file)
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    try:
        df = pd.read_csv(file)
        
        required_columns = ['timestamp', 'metric']
        if not all(col in df.columns for col in required_columns):
            return jsonify({"error": f"CSV file must contain columns: {', '.join(required_columns)}"}), 400
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.dropna(subset=['timestamp'])
        
        df = detect_anomalies(df, 'metric')
        result = {
            "timestamp": df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
            "metric": df['metric'].tolist(),
            "anomaly_flag": df['anomaly_flag'].tolist()
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
