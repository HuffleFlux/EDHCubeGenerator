# 2EDHCUBE + TAGS.py
import os
import json
import random
import requests
import unicodedata

# Paths
current_directory = os.path.dirname(os.path.abspath(__file__))
cube_basics_path = os.path.join(current_directory, "2CubeBasics.txt")
all_commanders_path = os.path.join(current_directory, "2AllCommanders.txt")
local_mtgjson_path = os.path.join(current_directory, "AllPrintings.json")
output_path = os.path.join(current_directory, "2CommanderCubeList.txt")

commander_sets = {"C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "CMA", "CMR", "CLB", "ONC", "VOC", "PIP"}
masters_draft_innovation_sets = {"2XM", "A25", "EMA", "IMA", "MM3", "MM2", "MMA", "UMA", "40K", "JMP", "BBD", "CMM"}

unique_cards = set()
cube_list = []

def format_commander_name(name):
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8')
    return name.split(" // ")[0].lower().replace(",", "").replace("'", "").replace(" ", "-")

def add_card(card_name):
    if card_name not in unique_cards:
        unique_cards.add(card_name)
        cube_list.append(card_name)

# Load CubeBasics
with open(cube_basics_path, "r", encoding="utf-8") as f:
    for line in f:
        card = line.strip()
        if card:
            card_name = card[2:] if card.startswith("1 ") else card
            add_card(card_name)

# Load commanders
with open(all_commanders_path, "r", encoding="utf-8") as f:
    all_lines = f.readlines()
all_commanders = [line.strip() for line in all_lines if line.strip() and not line.endswith(":")]
random.shuffle(all_commanders)
chosen_commanders = all_commanders[:20]

# Add commanders to cube
for commander in chosen_commanders:
    add_card(commander)

# Load MTGJSON
with open(local_mtgjson_path, "r", encoding="utf-8") as f:
    all_printings = json.load(f)["data"]

# Map of card name -> color identity
color_identity_lookup = {}
for set_data in all_printings.values():
    for card in set_data["cards"]:
        name = card.get("name")
        if name and "colorIdentity" in card:
            color_identity_lookup[name] = card["colorIdentity"]

# Fetch synergy cards and debug info
def fetch_edhrec_cards(commander):
    url = f"https://json.edhrec.com/pages/commanders/{format_commander_name(commander)}.json"
    print(f"🔍 EDHREC: {commander}")
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()

        # Color identity from MTGJSON fallback
        identity = color_identity_lookup.get(commander, [])
        color_identity = "".join(sorted(identity)) if identity else "Colorless"

        # Tags: from panels > taglinks
        taglinks = data.get("panels", {}).get("taglinks", [])
        top_tag = taglinks[0]["value"] if taglinks else "Unknown"

        print(f"🎨 Identity: {color_identity} | 🏷️ Top Tag: {top_tag}")

        # Extract cards
        json_dict = data.get("container", {}).get("json_dict", {})
        all_cards = []
        seen = set()

        def add_unique(cards):
            for card in cards:
                name = card["name"]
                if name not in unique_cards and name not in seen:
                    all_cards.append(name)
                    seen.add(name)

        for section in json_dict.get("cardlists", []):
            tag = section.get("tag", "").lower()
            if tag in {"topcards", "highsynergycards"}:
                add_unique(section.get("cardviews", []))

        # If fewer than 20 synergy cards, pull from support categories
        if len(all_cards) < 20:
            print(f"✅ Fetching extra cards for this commander")
            for section in json_dict.get("cardlists", []):
                tag = section.get("tag", "").lower()
                if tag in {"creatures", "instants", "sorceries", "enchantments", "utilityartifacts", "utilitylands"}:
                    add_unique(section.get("cardviews", []))
                if len(all_cards) >= 20:
                    break

        return all_cards[:20]

    except Exception as e:
        print(f"❌ Error for {commander}: {e}")
        return []

# Add synergy/support cards
for commander in chosen_commanders:
    for card in fetch_edhrec_cards(commander):
        add_card(card)

# Filler pool from sets
filler_pool = set()
for code in commander_sets | masters_draft_innovation_sets:
    if code in all_printings:
        for card in all_printings[code]["cards"]:
            if "name" in card and not card.get("layout", "") == "token":
                filler_pool.add(card["name"])

# Fill to 500
while len(cube_list) < 500 and filler_pool:
    candidate = random.choice(list(filler_pool))
    if candidate not in unique_cards:
        add_card(candidate)

# Save output
with open(output_path, "w", encoding="utf-8") as f:
    for card in cube_list:
        f.write(f"{card}\n")

print(f"✅ Cube complete! {len(cube_list)} cards saved to {output_path}")
