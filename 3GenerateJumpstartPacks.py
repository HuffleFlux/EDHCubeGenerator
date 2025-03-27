import os
import random

# Get the current directory of the script
current_directory = os.path.dirname(os.path.abspath(__file__))
commanders_file_path = os.path.join(current_directory, '3AllJumpstartCommanders.txt')
output_file_path = os.path.join(current_directory, '3CommanderSelection.txt')

# Read the commander list
commanders = []
with open(commanders_file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Parse commanders (ignoring category headers)
for line in lines:
    line = line.strip()
    if line and ":" not in line:  # Ignore color category headers
        commanders.append(line)

# Ensure we have enough commanders
if len(commanders) < 20:
    raise ValueError("Not enough commanders in the file for a proper selection.")

# Randomly shuffle commanders
random.shuffle(commanders)

# Assign commanders to players
num_players = 4
commanders_per_player = 2
player_picks = {f"Player{i+1}": [] for i in range(num_players)}

# Distribute commanders among players
for i in range(num_players * commanders_per_player):
    player = f"Player{(i % num_players) + 1}"
    player_picks[player].append(commanders.pop())

# Draft Variant - Pick 5 random commanders for two rounds
draft_round_1 = random.sample(commanders, 5)
draft_round_2 = random.sample([c for c in commanders if c not in draft_round_1], 5)

# Write results to a new file
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    # Player picks
    for player, picks in player_picks.items():
        output_file.write(f"{player}:\n")
        output_file.write("\n".join(picks))
        output_file.write("\n\n")
    
    # Draft Variant
    output_file.write("DraftVariant:\n")
    output_file.write("\n".join(draft_round_1))
    output_file.write("\n\n")

    # Round 2
    output_file.write("Round 2:\n")
    output_file.write("\n".join(draft_round_2))
    output_file.write("\n\n")

print(f"Commander selections have been written to {output_file_path}")
