import argparse
import csv
import socket
import signal
from contextlib import contextmanager
import requests

def raise_error(signum, frame):
    raise OSError

@contextmanager
def set_signal(signum, handler):
    old_handler = signal.getsignal(signum)
    signal.signal(signum, handler)
    try:
        yield
    finally:
        signal.signal(signum, old_handler)

@contextmanager
def set_alarm(time):
    signal.setitimer(signal.ITIMER_REAL, time)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)

@contextmanager
def raise_on_timeout(time):
    with set_signal(signal.SIGALRM, raise_error):
        with set_alarm(time):
            yield

def get_ip_address(domain):
    try:
        with raise_on_timeout(1):
            return socket.gethostbyname(domain)
    except:
        return "Unknown"

def get_ip_info(ip):
    url = f"https://ipinfo.io/{ip}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            isp = data.get('org', 'N/A')
            city = data.get('city', 'N/A')  # Extract the city
            country = data.get('country', 'N/A')
            return isp, city, country
    except requests.RequestException:
        pass
    return 'N/A', 'N/A', 'N/A'

def read_input_file(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip header
        return [row[0].strip() for row in reader if row]

def process_data(input_data, get_ip=True, get_info=True):
    results = []
    for item in input_data:
        row = [item]
        ip = get_ip_address(item) if get_ip else item
        row.append(ip)
        if get_info:
            isp, city, country = get_ip_info(ip)
            row.extend([isp, city, country])  # Adjust the order of ISP, City, Country
        results.append(row)
    return results

def save_to_csv(filename, data, headers):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)

def main():
    parser = argparse.ArgumentParser(description='Process hostnames/IPs and retrieve IP, ASN, City, and Country information.')
    parser.add_argument('-f', '--file', required=True, help='Input CSV file containing hostnames or IPs')
    parser.add_argument('--all', action='store_true', help='Perform all functions (get IP, ASN, City, and Country)')
    parser.add_argument('--ip', action='store_true', help='Only return IPs from hostnames')
    args = parser.parse_args()

    input_data = read_input_file(args.file)

    if args.all:
        results = process_data(input_data, get_ip=True, get_info=True)
        headers = ['Input', 'IP', 'ISP', 'City', 'Country']  # Updated header order
    elif args.ip:
        results = process_data(input_data, get_ip=True, get_info=False)
        headers = ['Input', 'IP']
    else:
        print("Please specify either --all or --ip flag.")
        return

    output_filename = f"{args.file.split('.')[0]}_output.csv"
    save_to_csv(output_filename, results, headers)
    print(f"Results saved to {output_filename}")

if __name__ == "__main__":
    main()
