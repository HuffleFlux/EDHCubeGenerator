import os
import json
import random

# Paths
current_directory = os.path.dirname(os.path.abspath(__file__))
lands_file_path = os.path.join(current_directory, '3Landbases.txt')
half_deck_file_path = os.path.join(current_directory, '3CommanderHalfDecks.txt')
mtgjson_file_path = os.path.join(current_directory, 'AllPrintings.json')  # Ensure this contains all card data
output_file_path = os.path.join(current_directory, '3JumpstartDecks.txt')

# Always store color identity in **W, U, B, R, G order**
color_identity_mapping = {
    "W": "White", "U": "Blue", "B": "Black", "R": "Red", "G": "Green",
    "WU": "Azorius", "UB": "Dimir", "BR": "Rakdos", "RG": "Gruul", "WG": "Selesnya",
    "WB": "Orzhov", "UR": "Izzet", "BG": "Golgari", "WR": "Boros", "UG": "Simic",
    "WUB": "Esper", "UBR": "Grixis", "BRG": "Jund", "WRG": "Naya", "WUG": "Bant",
    "WBG": "Abzan", "WUR": "Jeskai", "UBG": "Sultai", "WBR": "Mardu", "URG": "Temur",
    "WUBR": "NoGreen", "WBRG": "NoBlue", "UBRG": "NoWhite", "WUBG": "NoRed", "WURG": "NoBlack"
}

# Define fixed W, U, B, R, G order
color_order = ["W", "U", "B", "R", "G"]

# Basic land types
basic_lands = {
    "W": "Plains", "U": "Island", "B": "Swamp", "R": "Mountain", "G": "Forest"
}

# Load Lands.txt
def load_lands():
    """Reads the lands from Lands.txt and organizes them by category."""
    with open(lands_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    lands_by_category = {}
    current_category = None

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.endswith(":"):
            current_category = line[:-1]  # Remove colon
            lands_by_category[current_category] = []
        elif current_category:
            lands_by_category[current_category].append(line)

    return lands_by_category

lands_by_category = load_lands()

# Load MTGJSON Data
with open(mtgjson_file_path, 'r', encoding='utf-8') as file:
    mtgjson_data = json.load(file)

def get_commander_color_identity(commander_name):
    """Fetches the color identity of a commander from MTGJSON."""
    for set_data in mtgjson_data["data"].values():
        for card in set_data["cards"]:
            if card.get("name") == commander_name:
                color_identity = set(card.get("colorIdentity", []))
                print(f"🔹 {commander_name} color identity: {color_identity}")  # Debugging output
                return color_identity
    print(f"⚠️ WARNING: Color identity not found for {commander_name}")  # Debugging output
    return set()  # Return an empty set if not found

# Function to determine the land category based on sorted color identity
def get_land_category(color_identity):
    sorted_identity = "".join([c for c in color_order if c in color_identity])  # Sort in W, U, B, R, G order
    land_category = color_identity_mapping.get(sorted_identity, "Unknown")
    print(f"🟢 FINAL Combined Color Identity (Sorted): {sorted_identity} → Land Category: {land_category}")  # Debugging output
    return land_category

# Function to select 15 lands from Lands.txt
def select_lands(color_identity):
    category = get_land_category(color_identity)
    if category in lands_by_category:
        lands = lands_by_category[category]
        return random.sample(lands, min(15, len(lands)))
    return ["Could not find enough lands, please check Lands.txt."]

# Function to add basic lands (even split, if uneven one color gets +1)
def select_basic_lands(color_identity):
    color_list = [c for c in color_order if c in color_identity]  # Sort in W, U, B, R, G order
    
    if len(color_list) == 1:
        return [basic_lands[color_list[0]]] * 15
    elif len(color_list) == 2:
        return [basic_lands[color_list[0]]] * 8 + [basic_lands[color_list[1]]] * 7
    elif len(color_list) == 3:
        return [basic_lands[color_list[0]]] * 5 + [basic_lands[color_list[1]]] * 5 + [basic_lands[color_list[2]]] * 5
    elif len(color_list) == 4:
        return [basic_lands[color_list[0]]] * 4 + [basic_lands[color_list[1]]] * 4 + [basic_lands[color_list[2]]] * 4 + [basic_lands[color_list[3]]] * 3
    return ["Basic land selection failed."]

# Read decks from CommanderHalfDecks.txt
with open(half_deck_file_path, 'r', encoding='utf-8') as file:
    deck_data = file.read()

# Process each deck and add lands at the end
final_decks = ""
sections = deck_data.split("\n========================================\n")

for section in sections:
    lines = section.strip().split("\n")

    if len(lines) < 3:  # Skip empty sections or malformed data
        continue

    commander1 = lines[1].strip()  # First line is first commander
    commander2 = lines[2].strip()  # Second line is second commander
    print(f"🔎 Processing Deck: {commander1} + {commander2}")  # Debugging output

    # Fetch color identity for both commanders
    color_identity1 = get_commander_color_identity(commander1)
    color_identity2 = get_commander_color_identity(commander2)

    # Ensure both are fetched before merging
    if not color_identity1:
        print(f"⚠️ ERROR: {commander1} has no detected color identity, assuming empty set.")
    if not color_identity2:
        print(f"⚠️ ERROR: {commander2} has no detected color identity, assuming empty set.")

    # Combine and sort color identities before looking up land category
    combined_color_identity = {c for c in color_identity1 | color_identity2}  # Merge sets
    sorted_color_identity = "".join([c for c in color_order if c in combined_color_identity])  # Ensure sorting in WUBRG order
    print(f"🎨 {commander1} Identity: {color_identity1}, {commander2} Identity: {color_identity2}")
    print(f"🟢 FINAL Combined Color Identity (Sorted): {sorted_color_identity}")

    # Select lands
    selected_lands = select_lands(sorted_color_identity)
    basic_lands_added = select_basic_lands(sorted_color_identity)

    # Append final deck with lands
    final_decks += "\n".join(lines) + "\n"
    final_decks += "\n".join(selected_lands) + "\n"
    final_decks += "\n".join(basic_lands_added) + "\n"
    final_decks += "\n========================================\n"

# Save final decks
with open(output_file_path, 'w', encoding='utf-8') as file:
    file.write(final_decks)

print(f"✅ Final decks saved to {output_file_path}!")
