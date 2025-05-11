import requests

def deliver_webhook(subscription, payload):
    try:
        response = requests.post(subscription.target_url, json=payload, timeout=5)
        print("Delivered:", response.status_code)
    except Exception as e:
        print("Delivery failed:", str(e))
