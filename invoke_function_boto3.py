import boto3
import json

# Initialize a session using your AWS credentials
session = boto3.Session()

# Create a Lambda client
lambda_client = session.client("lambda")

# Define the payload
payload = {"name": "athreya", "email": "athreyac4@gmail.com"}
payload = {"name": "🔶Lama2.  G t 12 withdrwl  >> https: ", "email": "lama2@hexmos.com"}

# Invoke the Lambda function
response = lambda_client.invoke(
    FunctionName="bot_detect_model_lambda",
    InvocationType="RequestResponse",  # Synchronous invocation
    Payload=json.dumps(payload),
)

# Check if the invocation was successful
if "Payload" in response:
    # Decode the response payload
    decoded_payload = json.loads(response["Payload"].read().decode("utf-8"))

    # Print the response
    print(decoded_payload)
else:
    print("Error invoking Lambda function:", response)
