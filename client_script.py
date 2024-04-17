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
from tqdm import tqdm

# Your white list of manufacturers
white_list = config.white_list
dashboard = DashboardAPI(config.api_key, output_log=False, print_console=False)

networks = dashboard.organizations.getOrganizationNetworks(config.org_id)

# Initialize lists to hold clients
white_list_clients = []
black_list_clients = []

for network in networks:
    devices = dashboard.networks.getNetworkDevices(network['id'])
    for device in devices:
        if device['model'].startswith('MS') or device['model'].startswith('C9'):
            clients = dashboard.networks.getNetworkClients(network['id'], timespan=2678400, recentDeviceConnections='Wired')
            for client in tqdm(clients, desc=f"Processing clients for device {device['model']}"):
                manufacturer = client.get('manufacturer', 'N/A')
                if manufacturer == None:
                    manufacturer = 'N/A'
                # Check if the manufacturer is in the white list and categorize the client accordingly
                if manufacturer in white_list:
                    white_list_clients.append(client)
                else:
                    black_list_clients.append(client)

# Function to write clients to a CSV file
def write_clients_to_csv(clients, file_name):
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        # Writing headers
        if clients:
            writer.writerow(clients[0].keys())
        for client in clients:
            writer.writerow(client.values())

# Write the white list and black list clients to separate CSV files
write_clients_to_csv(white_list_clients, 'white_list_clients.csv')
write_clients_to_csv(black_list_clients, 'black_list_clients.csv')
