from flask import Flask, request, jsonify
import boto3
import re

app = Flask(__name__)

session = boto3.Session(
    aws_access_key_id='ASIA4EC2NDI3J5UKS775',
    aws_secret_access_key='dbXdxn5EqW2Nm7/cimcah35MATaLMJoBkXgK5adW',
    aws_session_token='FwoGZXIvYXdzECUaDIeamJ+ouBO9X67GkSK/AfQr2imJg5WjZaLH50yik6n1MEKB3AcYjxNGMOv6peBTiqD99PgY73lWip0agYxjZaQqeLOmzfUvpivx0HvsDSybuIwDG9QC5Z+MmM3FjQXt9AS7VWRqzMCNGF5BqfQMs0Ko5JIDO96KhxG1nwUn5kxm745b10qQzn5rZL5NBZ5NngCvx9oZaNIL6kWSJSnr2dRiBZssyskWG56k50RiahM1D95tM3aJeIBhFwn2f6A8Z52AYe21ElP3vbHteGUvKNLMpKkGMi2/xkVAa5qwNaGKO4wjB7p5kMKOGhYDuZ+wN3f6W57YL7VnC5QUOTt7vM9WfFs='
)

s3 = session.resource('s3')

s3client = session.client('s3')

bucket_name = 'b00937694-csci5409-bucket'

# To store the data received from the other app
stored_data = ''

@app.route('/start', methods=['POST'])
def start():
    data = request.get_json()
    
    # Record the IP
    ip = request.remote_addr
    
    return jsonify({"banner": "B00937694", "status_code":200})

@app.route('/store-data', methods=['POST'])
def store_data():
    data = request.get_json()
    global stored_data
    stored_data = data['data']
    print(stored_data)
    # Store data in AWS S3
    file_name = 'data.txt'
    s3client.put_object(Bucket=bucket_name, Key=file_name, Body=stored_data)
    
    return jsonify({"s3uri": f"https://{bucket_name}.s3.amazonaws.com/{file_name}"})

@app.route('/append-data', methods=['POST'])
def append_data():
    data = request.get_json()
    
    # Append data to the stored file on AWS S3
    file_name = 'data.txt'
    s3client.get_object(Bucket=bucket_name, Key=file_name)
    global stored_data
    print(stored_data)
    stored_data += data['data']
    print(stored_data)
    s3client.put_object(Bucket=bucket_name, Key=file_name, Body=stored_data)
    
    return jsonify({"message": "Data appended successfully"})

@app.route('/search-data', methods=['POST'])
def search_data():
    data = request.get_json()
    regex = data['regex']

    # Retrieve the file from AWS S3
    file_name = 'data.txt'
    response = s3client.get_object(Bucket=bucket_name, Key=file_name)
    file_content = response['Body'].read().decode('utf-8')
    print("file content is"+file_content)
    print(regex)
    
    lines = file_content.split('\n')
    result = None
    print(lines)

    for line in lines:
        if re.search(regex, line):
            result = line
            break 

    if result:
        found = True
    else:
        found = False

    return jsonify({"found": found, "result": result})

@app.route('/delete-file', methods=['POST'])
def delete_file():
    data = request.get_json()
    file_url = data['s3uri']
    print(file_url)
    # Extract the file key from the URL
    file_key = file_url.split('/')[-1]
    print(file_key)
    # Delete the file from AWS S3
    s3client.delete_object(Bucket=bucket_name, Key=file_key)
    
    return jsonify({"s3uri": f"https://{bucket_name}.s3.amazonaws.com/{file_key}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
