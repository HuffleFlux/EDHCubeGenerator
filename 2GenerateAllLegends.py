import os
import json
import requests

# Output path
current_directory = os.path.dirname(os.path.abspath(__file__))
output_file_path = os.path.join(current_directory, '2AllCommanders.txt')

# Fetch AllPrintings.json from MTGJSON
print("🌐 Fetching AllPrintings.json...")
url = "https://mtgjson.com/api/v5/AllPrintings.json"

try:
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    data = response.json()
    print("✅ Successfully retrieved MTGJSON data!")
except requests.exceptions.RequestException as e:
    print(f"❌ ERROR: Could not fetch AllPrintings.json: {e}")
    exit(1)

# Store unique valid commanders
valid_commanders = set()

# Traverse card data
for set_data in data["data"].values():
    for card in set_data.get("cards", []):
        leadership = card.get("leadershipSkills", {})
        legality = card.get("legalities", {})

        if leadership.get("commander") is True and legality.get("commander") == "Legal":
            name = card.get("name")
            if name:
                valid_commanders.add(name)

# Output results
with open(output_file_path, 'w', encoding='utf-8') as file:
    file.write("All Commanders:\n")
    file.write("\n".join(sorted(valid_commanders)))

print(f"✅ Found {len(valid_commanders)} valid commanders.")
print(f"📁 Saved to: {output_file_path}")
