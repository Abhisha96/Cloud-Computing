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

@app.route('/get-temp', methods=['POST'])
def get_temperature():
    data = request.get_json()
    if 'file' in data and 'name' in data:
        file_name = data['file']
        name = data['name']
        try:
            latest_temp = {}
            file_path = os.path.join(PERSISTENT_VOLUME_PATH, file_name)
            if os.path.exists(file_path):
                temperature = get_latest_temperature(file_name, name, latest_temp)
                if temperature is not None:
                    return jsonify({
                        "file": file_name,
                        "error": "Input file not in CSV format."
                    }), 400
                else:
                    return jsonify({
                        "file": file_name,
                        "temperature": temperature
                    }), 200
            else:
                return jsonify({
                    "file": file_name,
                    "error": "File not found."
                }), 404
        except Exception as e:
            return jsonify({
                "file": None,
                "error": "Invalid JSON input."
            }), 400

 
def get_latest_temperature(file_name, name, latest_temp):
    #latest_temperature = 0
    try:
        with open(f'/somya_PV_dir/{file_name}', mode='r') as file:
            csv_reader = csv.DictReader(file, delimiter=',')
            for row in csv_reader:
                if row[0] == name:
                    latest_temp['temperature'] = int(row[3])
            return latest_temp
    except Exception as e:
        return None
""" 
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
        return jsonify({"file": None, "error": str(e)}), 500 """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6001)
