import os
import json
import random
import re  # regex for stripping numbers and "x"

# --- config ---
TARGET_POOL_SIZE = 125  # final pool size to output

# Get the current directory of the script
current_directory = os.path.dirname(os.path.abspath(__file__))
pool_file_path = os.path.join(current_directory, 'AllPrintings.json')

# Load the JSON data from AllPrintings.json
with open(pool_file_path, encoding="utf8") as user_file:
    all_data = json.load(user_file)

# Extract ONE entry per card name (exclude basic lands)
# If multiple printings exist, we keep the first one encountered.
unique_cards_by_name = {}
for set_info in all_data['data'].values():
    for card in set_info.get('cards', []):
        if 'Basic' in card.get('supertypes', []):
            continue  # skip basic lands
        name = card.get('name')
        if not name:
            continue
        # only keep the first time we see this name
        if name not in unique_cards_by_name:
            unique_cards_by_name[name] = card

# Our canonical “all cards” list, one per name
all_cards_unique = list(unique_cards_by_name.values())
all_names = set(unique_cards_by_name.keys())

def load_decklists():
    """Load decklists from text files in the same folder and strip numbers and 'x' from card names."""
    decklists = []
    for file_name in os.listdir(current_directory):
        if file_name.endswith('.txt') and file_name.startswith('1decklist_'):
            with open(os.path.join(current_directory, file_name), 'r', encoding='utf-8') as file:
                # Remove leading numbers, optional 'x' or 'X', and spaces
                deck = [re.sub(r'^\d+[xX]?\s+', '', line.strip()) for line in file.readlines() if line.strip()]
                decklists.append(deck)
    return decklists

def adjust_pool(cards_by_name, decklists, winning_cards):
    """
    Adjust the pool of cards based on played and unplayed cards, working by NAME.
    cards_by_name: dict name -> card (one printing per name)
    """
    # All names that appeared in any deck
    played_names = set(card_name for deck in decklists for card_name in deck)

    # Start from all cards (dict copy)
    pool = dict(cards_by_name)

    # Remove winning cards entirely
    for card_name in winning_cards:
        pool.pop(card_name, None)

    # Remove unplayed cards (keep only names that appeared in at least one deck)
    for card_name in list(pool.keys()):
        if card_name not in played_names:
            pool.pop(card_name, None)

    return pool  # still dict name->card

def sample_new_cards(existing_names, count):
    """Sample new unique card NAMES not already in the pool, then return their card dicts."""
    available_names = list(all_names - existing_names)
    if count <= 0 or not available_names:
        return []
    chosen_names = set(random.sample(available_names, min(count, len(available_names))))
    return [unique_cards_by_name[n] for n in chosen_names]

# Simulate a match with decklists and winning cards
decklists = load_decklists()
winning_cards = decklists[0] if decklists else []  # assume first deck won if any exist

if decklists:
    # Adjust based on match results -> dict name->card
    adjusted_pool_dict = adjust_pool(unique_cards_by_name, decklists, winning_cards)
else:
    adjusted_pool_dict = {}

# Replenish to TARGET_POOL_SIZE using names (no duplicate printings possible)
current_names = set(adjusted_pool_dict.keys())
cards_to_replenish = TARGET_POOL_SIZE - len(current_names)
new_cards = sample_new_cards(current_names, cards_to_replenish)

# Final pool as a list of card dicts (unique by name)
adjusted_pool = list(adjusted_pool_dict.values()) + new_cards

# Trim in case we overshot (shouldn't happen but safe)
adjusted_pool = adjusted_pool[:TARGET_POOL_SIZE]

# Output the adjusted pool to a new file (names only)
output_file_path = os.path.join(current_directory, '1AdjustedCardPool.txt')
with open(output_file_path, 'w', encoding='utf-8') as file:
    file.write("Adjusted Card Pool:\n")
    for card in adjusted_pool:
        file.write(f"{card['name']}\n")

print(f"Adjusted card pool written to {output_file_path}")
