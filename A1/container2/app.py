import json
import csv
import logging
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def load_and_parse_csv(file_name):
    try:
        with open(f'/etc/data/{file_name}', mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            data = list(csv_reader)
            return data
    except Exception as e:
        logging.error(f"Error loading CSV file: {str(e)}")
        return None

@app.route('/temperature-info', methods=['POST'])
def temperature_info():
    try:
        request_data = request.get_json()

        file_name = request_data['file']
        name = request_data['name']
        key = request_data['key']

        csv_data = load_and_parse_csv(file_name)

        if key == 'temperature':
            latest_temperature = None
            for row in csv_data:
                if row['name'] == name:
                    latest_temperature = int(row['temperature'])
            if latest_temperature is not None:
                return jsonify({"file": file_name, "temperature": latest_temperature})
            else:
                logging.error(f"Name not found in the CSV data: {name}")
                return jsonify({"file": file_name, "error": "Name not found in the CSV data."}), 404
        else:
            logging.error(f"Invalid key: {key}")
            return jsonify({"file": file_name, "error": "Invalid key."}), 400
        
    except Exception as e:
        logging.error(f"Internal server error: {str(e)}")
        return jsonify({"file": None, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6001)
