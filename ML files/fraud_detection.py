import time
from collections import defaultdict
from datetime import datetime, timedelta

# Configuration
REQUEST_THRESHOLD = 5
TIME_WINDOW_SECONDS = 60
ALERT_MESSAGE = "Potential Spam/Fraud detected from IP address: {}"
ALERT_RECIPIENTS = ["taitilchheda@gmail.com", "haadirakhangi@gmail.com"]

# Data Structures to Track Requests
ip_request_counts = defaultdict(int)
ip_request_timestamps = defaultdict(list)

# Additional Spam Detection Parameters
USER_AGENT_BLACKLIST = ["curl", "wget", "python-requests"]
REQUEST_RATE_THRESHOLD_PER_USER = 3
SUSPICIOUS_CONTENT_KEYWORDS = ["free ticket", "win prize", "limited offer"]

# Function to Simulate Request Handling
def process_request(ip_address, user_agent=None, request_data=None):
    timestamp = datetime.now()

    ip_request_counts[ip_address] += 1
    ip_request_timestamps[ip_address].append(timestamp)

    cutoff_time = timestamp - timedelta(seconds=TIME_WINDOW_SECONDS)
    ip_request_timestamps[ip_address] = [ts for ts in ip_request_timestamps[ip_address] if ts >= cutoff_time]
    ip_request_counts[ip_address] = len(ip_request_timestamps[ip_address])

    if ip_request_counts[ip_address] > REQUEST_THRESHOLD:
        alert_message = ALERT_MESSAGE.format(ip_address)
        send_alert(alert_message)
        print(f"Alert Triggered: {alert_message}")

    if user_agent and any(bad_ua in user_agent.lower() for bad_ua in USER_AGENT_BLACKLIST):
        alert_message = f"Suspicious User-Agent detected from IP {ip_address}: {user_agent}"
        send_alert(alert_message)
        print(f"Alert Triggered: {alert_message}")

    if request_data:
        if isinstance(request_data, dict) and any(keyword in str(value).lower() for value in request_data.values() for keyword in SUSPICIOUS_CONTENT_KEYWORDS):
            alert_message = f"Suspicious Content Keywords found in request from IP {ip_address}: {request_data}"
            send_alert(alert_message)
            print(f"Alert Triggered: {alert_message}")

        if 'user_id' in request_data:
            user_id = request_data['user_id']
            user_request_count = 0
            if user_request_count > REQUEST_RATE_THRESHOLD_PER_USER:
                alert_message = f"High request rate from user {user_id} (IP: {ip_address})"
                send_alert(alert_message)
                print(f"Alert Triggered: {alert_message}")

    print(f"Request processed from IP: {ip_address}, Count: {ip_request_counts[ip_address]}")
    print("-" * 20)

# Function to Send Alert
def send_alert(message):
    print(f"Sending Alert: {message}")

# Example Usage
if __name__ == "__main__":
    process_request("192.168.1.100", user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    time.sleep(1)
    process_request("192.168.1.100", user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    time.sleep(0.5)
    process_request("192.168.1.100", user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    time.sleep(0.8)
    process_request("192.168.1.100", user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    time.sleep(0.2)
    process_request("192.168.1.100", user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    time.sleep(0.3)
    process_request("192.168.1.100", user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    time.sleep(65)
    process_request("192.168.1.100", user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    time.sleep(1)
    process_request("192.168.1.100", user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    time.sleep(0.5)
    process_request("192.168.1.100", user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    time.sleep(0.8)
    process_request("192.168.1.100", user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    time.sleep(0.2)
    process_request("192.168.1.100", user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

    process_request("10.0.0.1", user_agent="curl/7.68.0")
    process_request("10.0.0.2", user_agent="python-requests/2.25.1")

    process_request("172.16.0.5", request_data={"query": "free tickets for concert"})
    process_request("172.16.0.6", request_data={"search_term": "win a prize"})

    process_request("192.168.1.101")
    process_request("192.168.1.102")