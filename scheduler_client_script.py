""" 
Copyright (c) 2024 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
           https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

from meraki import DashboardAPI
import config
import csv
import schedule
import time
from tqdm import tqdm

# Function to fetch and process clients
def fetch_and_process_clients():
    dashboard = DashboardAPI(config.api_key, output_log=False, print_console=False)
    networks = dashboard.organizations.getOrganizationNetworks(config.org_id)
    white_list_clients = []
    black_list_clients = []

    white_list = config.white_list

    for network in networks:
        devices = dashboard.networks.getNetworkDevices(network['id'])
        for device in devices:
            if device['model'].startswith('MS') or device['model'].startswith('C9'):
                clients = dashboard.networks.getNetworkClients(network['id'], timespan=2678400, recentDeviceConnections='Wired')
                for client in tqdm(clients, desc=f"Processing clients for device {device['model']}"):
                    manufacturer = client.get('manufacturer', 'N/A')
                    if manufacturer is None:
                        manufacturer = 'N/A'
                    if manufacturer in white_list:
                        white_list_clients.append(client)
                    else:
                        black_list_clients.append(client)

    # Write to CSV
    write_clients_to_csv(white_list_clients, 'white_list_clients.csv')
    write_clients_to_csv(black_list_clients, 'black_list_clients.csv')

# Function to write clients to a CSV file
def write_clients_to_csv(clients, file_name):
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        if clients:
            writer.writerow(clients[0].keys())
        for client in clients:
            writer.writerow(client.values())

# Schedule to run every week
schedule.every().week.do(fetch_and_process_clients)

# Schedule to run the client processing job monthly
# schedule.every().month.do(fetch_and_process_clients)

# Schedule to run the client processing job daily
# schedule.every().day.do(fetch_and_process_clients)

# Schedule to run the client processing job every Monday (useful for weekly reports at the start of the week)
# schedule.every().monday.do(fetch_and_process_clients)

# Schedule to run the client processing job every Friday at a specific time (e.g., 6:00 PM)
# schedule.every().friday.at("18:00").do(fetch_and_process_clients)

# Schedule to run the client processing job every hour (useful for high-frequency tasks)
# schedule.every().hour.do(fetch_and_process_clients)

# Schedule to run the client processing job every 30 minutes
# schedule.every(30).minutes.do(fetch_and_process_clients)

# Loop so that the schedule tasks keep running
while True:
    schedule.run_pending()
    time.sleep(1)
