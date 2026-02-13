import requests
import time
import json

# Create a session to maintain cookies
session = requests.Session()
base_url = 'http://192.168.137.201/rj'

# Step 1: Get protocol data to find the protocol ID for "new"
response = session.get(f'{base_url}/protocol_mgr.php', params={
    'func': 'printproto',
    'format': 'js'
})

proto_data = response.json()
print("Available protocols:")
for i, proto in enumerate(proto_data):
    print(f"  {i}: {proto['title']} (ID: {proto['id']})")

# Find the "new" protocol
new_protocol = None
for proto in proto_data:
    if proto['title'].lower() == 'new':
        new_protocol = proto
        break

if not new_protocol:
    print("Error: 'new' protocol not found!")
    exit()

print(f"\nSelected protocol: {new_protocol['title']} (ID: {new_protocol['id']})")

# Step 2: Get first stage data
stage_data = new_protocol['stagedata']

# Step 3: Start the floc control
response = session.get(f'{base_url}/floc_control.php', params={
    'command': 'run_floc'
})
print(f"Floc control started: {response.text}")

# Step 4: Set RPM for first stage
first_stage_rpm = stage_data[0]['rpm']
response = session.get(f'{base_url}/setrpm.php', params={
    'rpm': first_stage_rpm
})
print(f"RPM set to {first_stage_rpm}")

# Step 5: Set G-value for first stage
gval = round(0.1839 * (first_stage_rpm ** 1.4227))
response = session.get(f'{base_url}/setgval.php', params={
    'gval': gval
})
print(f"G-value set to {gval}")

print("\n✓ Test started successfully!")
print("Waiting 5 seconds before stopping...")

# WAIT 5 SECONDS
time.sleep(5)

# STOP THE TEST
print("\nStopping test...")

# Stop floc control
response = session.get(f'{base_url}/floc_control.php', params={
    'command': 'stop_floc'
})
print(f"Floc control stopped: {response.text}")

# Set RPM to 0
response = session.get(f'{base_url}/setrpm.php', params={'rpm': 0})
print("RPM set to 0")

# Set G-value to 0
response = session.get(f'{base_url}/setgval.php', params={'gval': 0})
print("G-value set to 0")

print("\nTest stopped successfully!")