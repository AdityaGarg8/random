import json

# Define the new links
new_link1 = "https://github.com/t2linux/T2-Ubuntu/releases/download/v6.9.6-1/ubuntu-22.04-6.9.6-t2-jammy.iso.00"
new_link2 = "https://github.com/t2linux/T2-Ubuntu/releases/download/v6.9.6-1/ubuntu-22.04-6.9.6-t2-jammy.iso.01"

# Load the JSON file
with open('distro-metadata.json', 'r') as file:
    data = json.load(file)

# Function to update the links
def update_links(distros, name, new_links):
    for distro in distros:
        if distro['name'] == name:
            distro['iso'] = new_links

# Update the Ubuntu 22.04 - Jammy Jellyfish links
update_links(data['all'], "Ubuntu 22.04 - Jammy Jellyfish", [new_link1, new_link2])

# Save the updated JSON back to the file
with open('distro-metadata.json', 'w') as file:
    json.dump(data, file, indent=2)

print("Links updated successfully.")
