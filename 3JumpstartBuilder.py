import os
import json
import requests
import random
import subprocess
import unicodedata  # Import for character normalization

# Paths
current_directory = os.path.dirname(os.path.abspath(__file__))
commanders_file_path = os.path.join(current_directory, '3CommanderSelection.txt')
mtgjson_file_path = os.path.join(current_directory, 'AllPrintings.json')  # Local MTGJSON data
output_file_path = os.path.join(current_directory, '3CommanderHalfDecks.txt')

# Function to format commander names for EDHREC API
def format_commander_name(name):
    """Removes accents and formats commander names for EDHREC API."""
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8')  # Remove accents
    return name.split(" // ")[0].lower().replace(",", "").replace("'", "").replace(" ", "-")

# Function to fetch commander data from EDHREC
def fetch_edhrec_data(commander):
    edhrec_name = format_commander_name(commander)
    url = f"https://json.edhrec.com/pages/commanders/{edhrec_name}.json"
    print(f"🔍 Fetching: {commander} (EDHREC name: {edhrec_name})")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        print(f"❌ Failed to fetch {commander}")
        return None

# Load MTGJSON Data (Local)
def load_mtgjson():
    """Loads MTGJSON data to pull random cards from the correct color identity."""
    with open(mtgjson_file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

mtgjson_data = load_mtgjson()

# Fetch all nonland cards by color identity
def get_random_cards_by_color(color_identity, count=10, card_type=None):
    """Gets random cards from MTGJSON that match a given color identity and type."""
    matching_cards = []

    for set_data in mtgjson_data["data"].values():
        for card in set_data["cards"]:
            if "colorIdentity" in card and set(card["colorIdentity"]) == color_identity:
                if card_type == "land" and "Land" in card.get("types", []) and "Basic" not in card.get("supertypes", []):
                    matching_cards.append(card["name"])
                elif card_type == "nonland" and "Land" not in card.get("types", []):
                    matching_cards.append(card["name"])

    if len(matching_cards) < count:
        print(f"⚠️ WARNING: Not enough matching {card_type} cards for {color_identity}. Found {len(matching_cards)}.")

    return random.sample(matching_cards, min(count, len(matching_cards)))

# Read commander list
print("\n📂 Reading commander list...")
commanders = []
with open(commanders_file_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not any(keyword in line for keyword in ["Player", "DraftVariant", "Round"]):
            commanders.append(line)

if not commanders:
    print("❌ No commanders found!")
    exit()

print(f"✅ Found {len(commanders)} commanders!")

# Pair up commanders (2 per deck)
paired_commanders = [commanders[i:i+2] for i in range(0, len(commanders), 2)]

# Function to extract cards
def extract_cards(data):
    json_dict = data.get("container", {}).get("json_dict", {})
    categories = {
        "highsynergycards": "High Synergy Cards",
        "topcards": "Top Cards",
        "utilitylands": "Utility Lands",
        "creatures": "Creatures",
        "instants": "Instants",
        "sorceries": "Sorceries",
        "enchantments": "Enchantments",
        "utilityartifacts": "Utility Artifacts",
        "manaartifacts": "Mana Artifacts",
    }
    categorized_cards = {category: [] for category in categories.values()}

    for cardlist in json_dict.get("cardlists", []):
        tag = cardlist.get("tag", "").lower()
        header = categories.get(tag, None)
        if header and "cardviews" in cardlist:
            for card in cardlist["cardviews"]:
                categorized_cards[header].append(card["name"])

    return categorized_cards

formatted_output = ""

for commander_pair in paired_commanders:
    if len(commander_pair) < 2:
        continue  # Ignore unpaired commanders

    commander1, commander2 = commander_pair
    data1 = fetch_edhrec_data(commander1)
    data2 = fetch_edhrec_data(commander2)

    if not data1 and not data2:
        continue  # Skip if both failed

    formatted_output += f"Commanders:\n{commander1}\n{commander2}\n\nDeck:\n"

    deck1 = extract_cards(data1) if data1 else {key: [] for key in extract_cards({}).keys()}
    deck2 = extract_cards(data2) if data2 else {key: [] for key in extract_cards({}).keys()}

    def build_half_deck(deck, commander_name):
        """Builds a half-deck: 4 utility lands, all synergy/top cards, and 30 total nonlands.
        If not enough cards exist, fetches random cards from MTGJSON."""
        half_deck = []
        
        # Add utility lands (if not enough, fetch from MTGJSON)
        utility_lands = random.sample(deck["Utility Lands"], min(4, len(deck["Utility Lands"])))
        if len(utility_lands) < 4:
            missing_lands = 4 - len(utility_lands)
            color_identity = get_commander_color_identity(commander_name)
            print(f"⚠️ {commander_name} missing {missing_lands} utility lands, adding from MTGJSON...")
            utility_lands += get_random_cards_by_color(color_identity, missing_lands, card_type="land")
        
        half_deck += utility_lands
        half_deck += deck["Top Cards"]
        half_deck += deck["High Synergy Cards"]

        # Add nonlands until there are 30 total nonland cards
        nonland_pool = (deck["Creatures"] + deck["Instants"] + deck["Sorceries"] +
                        deck["Enchantments"] + deck["Utility Artifacts"])
        random.shuffle(nonland_pool)

        needed_nonlands = 30 - (len(deck["Top Cards"]) + len(deck["High Synergy Cards"]))
        half_deck += nonland_pool[:needed_nonlands]

        if len(half_deck) < 34:  # 30 nonlands + 4 utility lands
            # Fetch color identity for missing cards
            color_identity = get_commander_color_identity(commander_name)
            missing_count = 34 - len(half_deck)
            print(f"⚠️ {commander_name} missing {missing_count} nonland cards, adding from MTGJSON...")
            half_deck += get_random_cards_by_color(color_identity, missing_count, card_type="nonland")

        return half_deck

    # Function to get commander color identity from MTGJSON
    def get_commander_color_identity(commander_name):
        for set_data in mtgjson_data["data"].values():
            for card in set_data["cards"]:
                if card.get("name") == commander_name:
                    return set(card.get("colorIdentity", []))
        return set()  # Return empty set if not found

    formatted_output += "\n".join(build_half_deck(deck1, commander1) + build_half_deck(deck2, commander2)) + "\n\n"
    formatted_output += "=" * 40 + "\n\n"

# Save output
with open(output_file_path, 'w', encoding='utf-8') as file:
    file.write(formatted_output)

print(f"✅ Half-decks saved to {output_file_path}!")

# 🔹 Call JumpstartLandAdder.py to finish the decks
print("\n🚀 Running JumpstartLandAdder to finalize decks...")
subprocess.run(["python", os.path.join(current_directory, "3JumpstartLandAdder.py")])
