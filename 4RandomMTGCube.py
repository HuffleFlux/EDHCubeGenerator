import json
import random

# Load the JSON data from the AllPrintings.json file
with open(r'C:\Users\felix\Desktop\MTGJSON\AllPrintings.json', encoding="utf8") as user_file:
    all_data = json.load(user_file)

# Define set codes for specific categories
commander_sets = {'CMD', 'C13', 'C14', 'C15', 'C16', 'C17', 'C18', 'C19', 'C20', 'C21', 'CMA', 'CM2', 'VOC', 'WHO', 'DMC', 'PIP', 'AFC', 'KHC', 'MOC', 'MIC', 'MKC', 'NEC', 'NCC', 'OTC', 'ONC', 'SCD', 'LTC', 'BRC', 'LCC', '40K', 'WOC', 'ZNC'}
masters_draft_innovation_sets = {'ACR', 'BBD', 'CMR', 'CLB', 'CNS', 'CN2', 'DBL', 'JMP', 'J22', 'MH1', 'H1R', 'MH2', 'MH3', 'AKR', 'CMM', 'DMR', '2XM', '2X2', 'EMA', 'IMA', 'KLR', 'A25', 'MMA', 'MM2', 'MM3', 'RVR', 'TSR', 'PLST', 'UMA', 'SLX', 'VMA'}

# Extract all cards into a single list and classify them by set
all_cards = []
commander_cards = []
masters_draft_cards = []
for set_info in all_data['data'].values():
    for card in set_info['cards']:
        if 'Basic' not in card.get('supertypes', []):  # Exclude basic lands
            all_cards.append(card)
            if set_info['code'] in commander_sets:
                commander_cards.append(card)
            elif set_info['code'] in masters_draft_innovation_sets:
                masters_draft_cards.append(card)

def filter_cards(cards, condition):
    return [card for card in cards if condition(card)]

def create_commander_cube():
    selected_cards = set()  # To keep track of all selected card names to ensure uniqueness
    def sample_cards(source, count):
        sample = []
        while len(sample) < min(count, len(source)):
            card = random.choice(source)
            if card['name'] not in selected_cards:  # Check for uniqueness
                sample.append(card)
                selected_cards.add(card['name'])
        return sample

    # Filter and sample legendary creatures from all cards, not just commander sets
    all_legendary_creatures = filter_cards(all_cards, lambda x: 'Legendary' in x.get('supertypes', []) and 'Creature' in x.get('types', []))
    selected_legends = sample_cards(all_legendary_creatures, 48)

    # Continue with other specific categories
    selected_lands = sample_cards([c for c in all_cards if 'Land' in c.get('types', [])], 32)
    selected_commander_cards = sample_cards(commander_cards, 75)
    selected_masters_draft_cards = sample_cards(masters_draft_cards, 75)
    remaining_cards = [c for c in all_cards if c['name'] not in selected_cards]
    selected_other_cards = sample_cards(remaining_cards, 250)

    return selected_legends, selected_lands, selected_commander_cards, selected_masters_draft_cards, selected_other_cards

# Generate the cube
legendary_creatures, lands, commander_cards, draft_masters_cards, other_cards = create_commander_cube()

# Output to a text file
output_file_path = r'C:\Users\felix\Desktop\RandomCubeGenerator\RNGCube.txt'
with open(output_file_path, 'w', encoding='utf-8') as file:
    file.write("Legendary creatures:\n")
    file.writelines(f"{legend['name']}\n" for legend in legendary_creatures)
    file.write("\nLands:\n")
    file.writelines(f"{land['name']}\n" for land in lands)
    file.write("\nCommander Set Cards:\n")
    file.writelines(f"{card['name']}\n" for card in commander_cards)
    file.write("\nDraft or Masters Set Cards:\n")
    file.writelines(f"{card['name']}\n" for card in draft_masters_cards)
    file.write("\nRandom Cards:\n")
    file.writelines(f"{card['name']}\n" for card in other_cards)

print("Output written to RNGCommanderCube.txt")
