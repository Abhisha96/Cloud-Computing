import csv
import requests
import logging
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

container2_ip = 'http://k8-container2final:6001/'

storage_directory = "/root/abhisha_PV_dir"

file_data = {}

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
            data = list(csv_reader)
            return data
    except Exception as e:
        return jsonify({"file": file_name, "error": "Input file not in CSV Format."}), 500

@app.route('/store-file', methods=['POST'])
def store_file():
    try:
        request_data = request.get_json()
        file_name = request_data['file']
        file_data = request_data['data']
        
        if not file_name:
            return jsonify({"file": None, "error": "Invalid JSON input."}), 400

        if not file_data:
            return jsonify({"file": None, "error": "Invalid JSON input."}), 400

        # Store the data in the file
        with open(f'/root/abhisha_PV_dir/{file_name}', mode='w') as file:
            file.write(file_data)

        return jsonify({"file": file_name, "message": "Success."})
       
    except Exception as e:
        logging.error(f"Internal server error: {str(e)}")
        return jsonify({"file": file_name, "error": "Error while storing the file to the storage."}), 500

@app.route('/user-info', methods=['POST'])
def user_info():
    try:
        request_data = request.get_json()

        if not all(key in request_data for key in ['file', 'name', 'key']) or request_data['file'] is None:
            return jsonify({ "file": None,"error": "Invalid JSON input."}), 400

        file_name = request_data['file']
        name = request_data['name']
        key = request_data['key']

        current_directory = os.getcwd()
        print("Current Working Directory:", current_directory)

        print(os.path.exists(f'/root/abhisha_PV_dir/{file_name}'))

        if file_name is not None and not os.path.exists(f'/root/abhisha_PV_dir/{file_name}'):
            return jsonify({ "file": file_name,"error": "File not found."}), 400

        if not is_csv_file(file_name):
            return jsonify({"file": file_name, "error": "Input file not in CSV Format."}), 400
        
        csv_data = load_and_parse_csv(file_name)   
        if key == 'location':
            latest_location = None
            for row in csv_data:
                if row['name'] == name:
                    latest_location = {"latitude": float(row['latitude']), "longitude": float(row['longitude'])}
            if latest_location:
                return jsonify({"file": file_name, "latitude": latest_location["latitude"], "longitude": latest_location["longitude"]})
            else:
                return jsonify({"file": file_name, "error": "Name not found in the"+file_name}), 404

      #  elif key == 'temperature': 
       #     response = forward_to_container2(request_data)
        #    return jsonify(response)

        else:
            logging.error(f"Internal server error: {str(e)}")
            return jsonify({"file": file_name, "error": "Invalid 'key' value."}), 400

    except Exception as e:
        logging.error(f"Internal server error: {str(e)}")
        return jsonify({"file": file_name, "error": "Internal Server Error"}), 400
#
#def forward_to_container2(request_data):
 #   try:
  #      response = requests.post(f"{container2_ip}/temperature-info", json=request_data)
   #     return response.json()
    #except Exception as e:
     #   return {"file": request_data.get('file'), "error": "Not able to communicate with container2"}
    
@app.route('/get-temperature', methods=['POST'])
def temperature_info_c1():
    try:
        request_data = request.get_json()
        file_name = request_data['file']
        name = request_data['name']

        if not all(key in request_data for key in ['file', 'name']) or request_data['file'] is None:
            return jsonify({ "file": None,"error": "Invalid JSON input."}), 400
        
        if not os.path.exists(f'/root/abhisha_PV_dir/{file_name}'):
            return jsonify({ "file": file_name,"error": "File not found."}), 400

        if not is_csv_file(file_name):
            return jsonify({"file": file_name, "error": "Input file not in CSV Format."}), 400
    
        response = requests.post(f"{container2_ip}/temperature-info", json=request_data)
        return response.json()
    except Exception as e:
        logging.error(f"Internal server error: {str(e)}")
        return {"file": request_data.get('file'), "error": "Not able to communicate with container2"}
    
if __name__ == '__main__':
    # Start the Flask app
    app.run(host='0.0.0.0', port=6000, debug=True)