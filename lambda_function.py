import sys
import json
import os
import pickle
from datetime import datetime
import requests

WEBHOOK_CHANNEL_URL = "https://discord.com/api/webhooks//CGNhq6IpuvHnvez52IMoS6P3f98JbuQ5O6ZmpNtohGs6QXEOv2eKFcSXee5YRo2dV4F2"


lm_headers = {
    "Authorization": "Basic auth==",
    "Content-Type": "application/json",
}
LIST_MONK_URL = "https://lm.com"


def log_message(message):
    try:
        print("Log: " + message)
        with open("logs.txt", "a") as log_file:
            # Get the current time in a readable format (e.g., "2023-03-15 10:17:54")
            current_time = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            # Write the message to the log file with the current time
            print(f"{current_time} {message}", file=log_file)
    except Exception as e:
        print(e)


def send_discord_notification(
    message,
):  # this will send message regarding upcomming scheduled email in discord server
    payload = {"content": message}
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        WEBHOOK_CHANNEL_URL, data=json.dumps(payload), headers=headers
    )
    if response.status_code != 204:
        log_message(f"Failed to send Discord notification: {response.text}")


def fetch_subscriber_data(email):
    try:
        url = LIST_MONK_URL + "/api/subscribers"
        params = {"query": f"subscribers.email LIKE '%{email}%'"}
        response = requests.get(url, params=params, headers=lm_headers)
        if response.status_code == 200:
            data = response.json()
            da = data["data"]
            res = da["results"][0]
            subscriber_id = res["id"]
            return subscriber_id
        else:
            print(f"Request failed with status code {response.status_code}")
            return None
    except Exception as e:
        message = f"Problem while retrieving the BOT {email}"
        send_discord_notification(message)
        message += str(e)
        log_message(message)
        return None


def block_subscriber(subscriber_id):
    try:
        block_url = LIST_MONK_URL + f"/api/subscribers/{subscriber_id}/blocklist"
        response = requests.put(block_url, headers=lm_headers)
        block_res = response.json()
        if "data" in block_res and block_res["data"] == True:

            return True

        else:
            print("Failed to block subscriber")
            return False
    except Exception as e:
        message = f"Problem while blocking the BOT {subscriber_id}"
        send_discord_notification(message)
        message += str(e)
        log_message(message)
        return False


def block(email):
    subscriber_id = fetch_subscriber_data(email)
    if subscriber_id:
        return block_subscriber(subscriber_id)
    return False


def process_response(is_bot, name, email, block_resp):
    if is_bot:
        message = f"""Blocked BOT Sub to 365 Newsletter, Name: {name}, email: {email}"""
        send_discord_notification(message)
        return message, block_resp
    else:
        message = f"""New Sub to 365 Newsletter, Name: {name}, email: {email}"""
        send_discord_notification(message)
        print("Not a bot:", is_bot)
        return message, None


def handler(event, context):
    # Extract name and email from the event
    print("^^^Event ", event)

    if isinstance(event, str):
        print("Event is a string:", event)
        # Assuming the event is a raw JSON string, load it into a dictionary
        body = json.loads(event)
        print("Loaded body:", body)
        try:
            if "name" in body and body["name"] is not None:
                name = body["name"]
        except KeyError:
            print("No name")
        try:
            if "email" in body and body["email"] is not None:
                email = body["email"]
        except KeyError:
            print("No email")
    else:
        # If event is not a string, it's already a dictionary
        print("Event is a dictionary:", event)
        try:
            if "name" in event and event["name"] is not None:
                name = event["name"]
        except KeyError:
            print("No name")
        try:
            if "email" in event and event["email"] is not None:
                email = event["email"]
        except KeyError:
            print("No email")

    print("->>>>>>>>>>>>>", name)

    print("->>>>>>>>>>>>>", name)
    print(f"Current working directory: {os.getcwd()}")
    print(f"ls working directory: {os.listdir()}")

    local_file_path = "dt_model_file.pkl"
    print(f"Model file path: {os.path.abspath(local_file_path)}")

    # Load both the model and the vectorizer
    with open(local_file_path, "rb") as f:
        model_and_vectorizer = pickle.load(f)

    # Unpack the model and the vectorizer
    clf, vectorizer = model_and_vectorizer

    # Step 4: Make predictions
    data_to_test = name + email
    # Transform the new data using the loaded vectorizer
    data_to_test_transformed = vectorizer.transform([data_to_test])

    # Make a prediction
    prediction = clf.predict(data_to_test_transformed)

    # Print the prediction
    print("Prediction for data_to_test:", prediction[0])
    is_bot = True
    if prediction[0] == 0:
        is_bot = False

    if is_bot == False:
        message = f"""New Sub to 365 Newsletter, Name: {name}, email: {email}"""
        send_discord_notification(message)
        return json.dumps(
            {
                "data": {"name": name, "email": email},
            }
        )
    block_resp = block(email)
    message = f"""Blocked BOT Sub to 365 Newsletter, Name: {name}, email: {email}"""
    send_discord_notification(message)
    message, block_resp = process_response(is_bot, name, email, block_resp)
    # Return the result
    # return {"statusCode": 200, "data": {"bot": bot}}
    # Construct the response
    response = {
        "statusCode": 200,
        "data": {"bot": is_bot},
    }

    # Return the response as JSON
    return json.dumps(response)
