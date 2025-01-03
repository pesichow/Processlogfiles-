
import re
import csv
from collections import Counter, defaultdict
from datetime import datetime
import requests
import matplotlib.pyplot as plt

# Function to parse the log file and extract information
def parse_log_file(file_path):
    ip_requests = Counter()
    endpoint_requests = Counter()
    failed_logins = defaultdict(int)
    time_requests = Counter()

    with open(file_path, 'r') as file:
        for line in file:
            # Extract IP addresses
            ip_match = re.match(r"(\d+\.\d+\.\d+\.\d+)", line)
            if ip_match:
                ip = ip_match.group(1)
                ip_requests[ip] += 1

            # Extract endpoints
            endpoint_match = re.search(r'\"[A-Z]+ (\/\S*) HTTP\/1\.1\"', line)
            if endpoint_match:
                endpoint = endpoint_match.group(1)
                endpoint_requests[endpoint] += 1

            # Extract timestamps
            time_match = re.search(r'\[(\d+\/\w+\/\d+:\d+:\d+:\d+)', line)
            if time_match:
                timestamp = datetime.strptime(time_match.group(1), "%d/%b/%Y:%H:%M:%S")
                time_requests[timestamp.hour] += 1

            # Detect failed login attempts (HTTP 401 or "Invalid credentials")
            if ' 401 ' in line or 'Invalid credentials' in line:
                if ip_match:
                    failed_logins[ip] += 1

    return ip_requests, endpoint_requests, failed_logins, time_requests

# Function to get geolocation data for an IP
def get_geolocation(ip):
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        if response.status_code == 200:
            data = response.json()
            return data.get("city", "Unknown"), data.get("country", "Unknown")
    except Exception as e:
        print(f"Error fetching geolocation for IP {ip}: {e}")
    return "Unknown", "Unknown"

# Function to save results to a CSV file
def save_to_csv(ip_data, endpoint_data, suspicious_ips, time_data, output_file='log_analysis_results.csv'):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write IP requests
        writer.writerow(["IP Address", "Request Count", "City", "Country"])
        for ip, count in ip_data.items():
            city, country = get_geolocation(ip)
            writer.writerow([ip, count, city, country])

        # Write most accessed endpoint
        writer.writerow([])
        writer.writerow(["Endpoint", "Access Count"])
        for endpoint, count in endpoint_data.items():
            writer.writerow([endpoint, count])

        # Write suspicious activity
        writer.writerow([])
        writer.writerow(["IP Address", "Failed Login Count"])
        for ip, count in suspicious_ips.items():
            writer.writerow([ip, count])

        # Write time-based analysis
        writer.writerow([])
        writer.writerow(["Hour", "Request Count"])
        for hour, count in time_data.items():
            writer.writerow([hour, count])

# Function to plot data
def plot_data(ip_data, endpoint_data, time_data):
    # Bar chart for top IP addresses
    top_ips = ip_data.most_common(5)
    ips, counts = zip(*top_ips)
    plt.bar(ips, counts)
    plt.title("Top 5 IP Addresses by Requests")
    plt.xlabel("IP Address")
    plt.ylabel("Request Count")
    plt.show()

    # Bar chart for time-based analysis
    hours = list(time_data.keys())
    requests = list(time_data.values())
    plt.bar(hours, requests)
    plt.title("Requests by Hour")
    plt.xlabel("Hour")
    plt.ylabel("Request Count")
    plt.show()

# Main function to execute the analysis
def main():
    log_file = 'sample.log'
    threshold = 10  # Configurable threshold for failed login attempts

    ip_requests, endpoint_requests, failed_logins, time_requests = parse_log_file(log_file)

    # Identify the most accessed endpoint
    most_accessed = endpoint_requests.most_common(1)[0]

    # Identify suspicious IPs exceeding the threshold
    suspicious_ips = {ip: count for ip, count in failed_logins.items() if count > threshold}

    # Display results
    print("IP Address           Request Count")
    for ip, count in ip_requests.most_common():
        print(f"{ip:20} {count}")

    print("\nMost Frequently Accessed Endpoint:")
    print(f"{most_accessed[0]} (Accessed {most_accessed[1]} times)")

    print("\nSuspicious Activity Detected")
    for ip, count in suspicious_ips.items():
        print(f"{ip:20} {count}")

    print("\nRequests by Hour:")
    for hour, count in time_requests.items():
        print(f"{hour}:00 - {hour + 1}:00   {count} requests")

    # Save results to CSV
    save_to_csv(ip_requests, endpoint_requests, suspicious_ips, time_requests)

    # Plot data
    plot_data(ip_requests, endpoint_requests, time_requests)

if __name__ == "__main__":
    main()

"""*#Extra code *"""

import re
import csv
from collections import Counter, defaultdict
from datetime import datetime
import requests

# Function to parse the log file and extract information
def parse_log_file(file_path):
    ip_requests = Counter()
    endpoint_requests = Counter()
    failed_logins = defaultdict(int)
    time_analysis = Counter()

    with open(file_path, 'r') as file:
        for line in file:
            # Extract IP addresses
            ip_match = re.match(r"(\d+\.\d+\.\d+\.\d+)", line)
            if ip_match:
                ip = ip_match.group(1)
                ip_requests[ip] += 1

            # Extract endpoints
            endpoint_match = re.search(r'\"[A-Z]+ (\S+) HTTP/1\.1\"', line)
            if endpoint_match:
                endpoint = endpoint_match.group(1)
                endpoint_requests[endpoint] += 1

            # Detect failed login attempts (HTTP 401 or "Invalid credentials")
            if ' 401 ' in line or 'Invalid credentials' in line:
                if ip_match:
                    failed_logins[ip] += 1

            # Extract request time for time-based analysis
            time_match = re.search(r'\[(\d+/\w+/\d+:\d+:\d+:\d+) ', line)
            if time_match:
                time_str = time_match.group(1)
                request_time = datetime.strptime(time_str, '%d/%b/%Y:%H:%M:%S')
                time_analysis[request_time.hour] += 1

    return ip_requests, endpoint_requests, failed_logins, time_analysis

# Function to get geolocation information for an IP address
def get_geolocation(ip):
    try:
        response = requests.get(f"https://ipapi.co/{ip}/json/")
        data = response.json()
        city = data.get("city", "Unknown")
        country = data.get("country_name", "Unknown")
        return city, country
    except requests.RequestException:
        return "Unknown", "Unknown"

# Function to save results to a CSV file
def save_to_csv(ip_data, endpoint_data, suspicious_ips, time_data, output_file='analysis_results.csv'):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write IP requests sorted in descending order
        writer.writerow(["IP Address", "Request Count", "City", "Country"])
        sorted_ip_data = sorted(ip_data.items(), key=lambda x: x[1], reverse=True)
        for ip, count in sorted_ip_data:
            city, country = get_geolocation(ip)
            writer.writerow([ip, count, city, country])

        # Write most accessed endpoints sorted in descending order
        writer.writerow([])
        writer.writerow(["Endpoint", "Access Count"])
        sorted_endpoint_data = sorted(endpoint_data.items(), key=lambda x: x[1], reverse=True)
        for endpoint, count in sorted_endpoint_data:
            writer.writerow([endpoint, count])

        # Write suspicious activity sorted in descending order
        writer.writerow([])
        writer.writerow(["IP Address", "Failed Login Count"])
        sorted_suspicious_ips = sorted(suspicious_ips.items(), key=lambda x: x[1], reverse=True)
        for ip, count in sorted_suspicious_ips:
            writer.writerow([ip, count])

        # Write time-based analysis sorted by hour
        writer.writerow([])
        writer.writerow(["Hour", "Request Count"])
        sorted_time_data = sorted(time_data.items())
        for hour, count in sorted_time_data:
            writer.writerow([hour, count])

# Main function to execute the analysis
def main():
    log_file = 'sample.log'
    threshold = 10  # Configurable threshold for failed login attempts

    ip_requests, endpoint_requests, failed_logins, time_analysis = parse_log_file(log_file)

    # Identify the most accessed endpoint
    most_accessed = endpoint_requests.most_common(1)[0]

    # Identify suspicious IPs exceeding the threshold
    suspicious_ips = {ip: count for ip, count in failed_logins.items() if count > threshold}

    # Display results
    print("IP Address           Request Count")
    for ip, count in sorted(ip_requests.items(), key=lambda x: x[1], reverse=True):
        print(f"{ip:20} {count}")

    print("\nMost Frequently Accessed Endpoint:")
    print(f"{most_accessed[0]} (Accessed {most_accessed[1]} times)")

    print("\nSuspicious Activity Detected:")
    for ip, count in sorted(suspicious_ips.items(), key=lambda x: x[1], reverse=True):
        print(f"{ip:20} {count}")

    print("\nTime-Based Analysis:")
    for hour, count in sorted(time_analysis.items()):
        print(f"Hour {hour:02}: {count} requests")

    # Save results to CSV
    save_to_csv(ip_requests, endpoint_requests, suspicious_ips, time_analysis)

if __name__ == "__main__":
    main()
