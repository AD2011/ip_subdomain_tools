import argparse
import csv
import requests
import os

def get_ip_info(ip):
    url = f"https://ipinfo.io/{ip}/json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            isp = data.get('org', 'N/A')
            city = data.get('city', 'N/A')
            country = data.get('country', 'N/A')
            return isp, city, country
    except requests.RequestException:
        pass
    return 'N/A', 'N/A', 'N/A'

def read_input_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def save_to_csv(filename, data):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['IP', 'ISP', 'City', 'Country'])
        writer.writerows(data)

def main():
    parser = argparse.ArgumentParser(description='Retrieve ISP, City, and Country for a list of IPs.')
    parser.add_argument('-f', '--file', required=True, help='Input file containing IP addresses')
    args = parser.parse_args()

    input_data = read_input_file(args.file)
    results = [(ip, *get_ip_info(ip)) for ip in input_data]

    output_filename = f"{os.path.splitext(args.file)[0]}_output.csv"
    save_to_csv(output_filename, results)
    print(f"Results saved to {output_filename}")

if __name__ == "__main__":
    main()
