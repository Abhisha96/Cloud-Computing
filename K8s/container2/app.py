import json
import csv
import logging
import requests
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def is_csv_file(file_name):
    try:
        with open(f'/root/abhisha_PV_dir/{file_name}', mode='r') as csv_file:
               # Try different delimiters
            first_line = csv_file.readline()
            if ',' in first_line or ';' in first_line or '\t' in first_line:
                num_columns = len(first_line.split(','))
                if all(len(line.split(',')) == num_columns for line in csv_file):
                    return True
            return False
    except FileNotFoundError:
        return False


def load_and_parse_csv(file_name):
    try:
        with open(f'/root/abhisha_PV_dir/{file_name}', mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            return csv_reader
    except Exception as e:
        logging.error(f"Error loading CSV file: {str(e)}")
        return None

@app.route('/temperature-info', methods=['POST'])
def temperature_info():
    try:
        request_data = request.get_json()

        file_name = request_data['file']
        name = request_data['name']

        if not is_csv_file(file_name):
            return jsonify({"file": file_name, "error": "Input file not in CSV Format."}), 400
        
        csv_data = load_and_parse_csv(file_name)

        temperature_data = []
        for row in csv_data:
            if row['name'] == name:
                temperature_data.append({
                    'name': row['name'],
                    'temperature': row['temperature']
                })
        if not temperature_data:
            logging.error(f"No data found for name: {name}")
            return jsonify({"file": file_name, "error": f"No data found for name: {name}"}), 404

        return jsonify({"file": file_name, "temperature": temperature_data}),200
        
    except Exception as e:
        logging.error(f"Internal server error: {str(e)}")
        return jsonify({"file": file_name, "error": "Input file not in CSV Format."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6001)