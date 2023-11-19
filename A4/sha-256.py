import hashlib
import json
import requests

def lambda_handler(event, context):
    # Extract necessary information from the event
    banner = "B00937694"
    action = "sha256"  # Hardcoded as this is the SHA-256 Lambda function
    value = event['value']
    arn = "arn:aws:lambda:us-east-1:833413257782:function:SHA-256"

    # Perform SHA-256 hashing
    hashed_value = hash_sha256(value)

    # Prepare the result payload
    result_payload = {
        "banner": banner,
        "result": hashed_value,
        "arn": arn,
        "action": action,
        "value": value
    }

    # Send the result to the specified endpoint (/end)
    send_result_to_app(result_payload, "http://129.173.67.184:6000/end")

    return {
        'statusCode': 200,
        'body': json.dumps('Hashing complete!')
    }

def hash_sha256(data):
    # Perform SHA-256 hashing using hashlib
    sha256 = hashlib.sha256()
    sha256.update(data.encode('utf-8'))
    return sha256.hexdigest()

def send_result_to_app(result, app_url):
    # Send a POST request to the provided app_url
    response = requests.post(app_url, json=result)
    
    if response.status_code == 200:
        print("Result sent successfully")
    else:
        print(f"Failed to send result. Status code: {response.status_code}, Response: {response.text}")