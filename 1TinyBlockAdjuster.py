import os
import json
import random
import re  # Import regex for stripping numbers and "x"

# Get the current directory of the script
current_directory = os.path.dirname(os.path.abspath(__file__))
pool_file_path = os.path.join(current_directory, 'AllPrintings.json')

# Load the JSON data from AllPrintings.json
with open(pool_file_path, encoding="utf8") as user_file:
    all_data = json.load(user_file)

# Extract all cards into a single list, excluding basic lands
all_cards = []
for set_info in all_data['data'].values():
    for card in set_info['cards']:
        if 'Basic' not in card.get('supertypes', []):  # Exclude basic lands
            all_cards.append(card)

def load_decklists():
    """Load decklists from text files in the same folder and strip numbers and 'x' from card names."""
    decklists = []
    for file_name in os.listdir(current_directory):
        if file_name.endswith('.txt') and file_name.startswith('1decklist_'):
            with open(os.path.join(current_directory, file_name), 'r', encoding='utf-8') as file:
                # Use regex to remove leading numbers, optional 'x' or 'X', and spaces
                decklists.append([re.sub(r'^\d+[xX]?\s+', '', line.strip()) for line in file.readlines()])
    return decklists

def adjust_pool(cards, decklists, winning_cards):
    """Adjust the pool of cards based on played and unplayed cards."""
    # Convert card data to a dictionary for quick access
    card_dict = {card['name']: card for card in cards}

    # Collect all cards used in the decks
    played_cards = set(card for deck in decklists for card in deck)

    # Remove winning cards
    for card_name in winning_cards:
        card_dict.pop(card_name, None)

    # Remove unplayed cards (cards not in any deck)
    for card_name in list(card_dict.keys()):  # Use list to avoid runtime modification errors
        if card_name not in played_cards:
            card_dict.pop(card_name)

    return list(card_dict.values())

def generate_random_cards(cards, count):
    """Generate a list of unique random cards."""
    return random.sample(cards, min(count, len(cards)))  # Ensure we don't exceed available cards

# Simulate a match with decklists and winning cards
decklists = load_decklists()  # Load decklists from text files
winning_cards = decklists[0] if decklists else []  # Assume the first deck is the winner if decklists exist

# Adjust the pool of cards based on match results, only if decklists exist
if decklists:
    adjusted_pool = adjust_pool(all_cards, decklists, winning_cards)
else:
    adjusted_pool = []  # Start fresh if no decks are provided

# Calculate the number of cards to replenish to maintain exactly 100 cards
cards_to_replenish = 100 - len(adjusted_pool)

# Replenish the pool with new random cards
new_cards = generate_random_cards([card for card in all_cards if card not in adjusted_pool], cards_to_replenish)
adjusted_pool.extend(new_cards)

# Ensure the pool has exactly 100 cards
adjusted_pool = adjusted_pool[:100]

# Output the adjusted pool to a new file
output_file_path = os.path.join(current_directory, '1AdjustedCardPool.txt')
with open(output_file_path, 'w', encoding='utf-8') as file:
    file.write("Adjusted Card Pool:\n")
    file.writelines(f"{card['name']}\n" for card in adjusted_pool)

print(f"Adjusted card pool written to {output_file_path}")
