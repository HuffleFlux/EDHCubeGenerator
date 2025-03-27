import os
import json
import requests

# Define valid mono-color and two-color identities
COLOR_IDENTITIES = {
    "White": ["W"],
    "Blue": ["U"],
    "Black": ["B"],
    "Red": ["R"],
    "Green": ["G"],
    "Azorius": ["W", "U"],
    "Dimir": ["U", "B"],
    "Rakdos": ["B", "R"],
    "Gruul": ["R", "G"],
    "Selesnya": ["G", "W"],
    "Orzhov": ["W", "B"],
    "Izzet": ["U", "R"],
    "Golgari": ["B", "G"],
    "Boros": ["R", "W"],
    "Simic": ["G", "U"]
}

# Get the current directory of the script
current_directory = os.path.dirname(os.path.abspath(__file__))
output_file_path = os.path.join(current_directory, '3AllJumpstartCommanders.txt')

# Fetch the MTGJSON AllPrintings.json from the web
print("🌐 Fetching AllPrintings.json from MTGJSON...")
url = "https://mtgjson.com/api/v5/AllPrintings.json"

try:
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    data = response.json()
    print("✅ MTGJSON data successfully retrieved!")
except requests.exceptions.RequestException as e:
    print(f"❌ ERROR: Could not fetch AllPrintings.json: {e}")
    exit(1)

# Dictionary to store commanders by color category
commanders_by_color = {key: [] for key in COLOR_IDENTITIES.keys()}

# Extract valid commanders
for set_data in data["data"].values():
    for card in set_data["cards"]:
        # Ensure the card is legendary
        if "supertypes" not in card or "Legendary" not in card["supertypes"]:
            continue

        # Exclude legendary lands and artifacts
        if "types" in card and ("Land" in card["types"] or "Artifact" in card["types"]):
            continue

        # Must be legal in commander
        if "legalities" not in card or card["legalities"].get("commander") != "Legal":
            continue

        # Must be a legendary creature or planeswalker with commander text
        is_legal_commander = False
        if "types" in card and "Creature" in card["types"]:
            is_legal_commander = True
        elif "types" in card and "Planeswalker" in card["types"]:
            if "text" in card and "can be your commander" in card["text"].lower():
                is_legal_commander = True

        if not is_legal_commander:
            continue

        # Get color identity
        color_identity = card.get("colorIdentity", [])

        # Add to appropriate category
        for color_category, color_values in COLOR_IDENTITIES.items():
            if sorted(color_identity) == sorted(color_values):
                commanders_by_color[color_category].append(card["name"])
                break

# Write results to the output file
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    for color_category, commanders in commanders_by_color.items():
        output_file.write(f"{color_category}:\n")
        output_file.write("\n".join(sorted(set(commanders))))
        output_file.write("\n\n")

print(f"✅ All legal commanders have been written to {output_file_path}")
