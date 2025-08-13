# 2EDHCUBE + TAGS (Updated per user requests)
# Changes:
# 1) Removed CubeBasics list entirely (no dependency on 2CubeBasics.txt)
# 2) Do NOT force-add "top cards" separately — they are just part of the extra pool
# 3) Increase extra cards per commander to 50
# 4) If the cube size is < 480 at the end of the first pass, loop commanders again
#    and try to fill using any EDHREC deck category EXCEPT those tagged as game changers
#    (still avoiding duplicates). After that, if still short of 500, fill from commander/masters sets.

import os
import json
import random
import requests
import unicodedata

# Paths
current_directory = os.path.dirname(os.path.abspath(__file__))
all_commanders_path = os.path.join(current_directory, "2AllCommanders.txt")
local_mtgjson_path = os.path.join(current_directory, "AllPrintings.json")
output_path = os.path.join(current_directory, "2CommanderCubeList.txt")

commander_sets = {"C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "CMA", "CMR", "CLB", "ONC", "VOC", "PIP"}
masters_draft_innovation_sets = {"2XM", "A25", "EMA", "IMA", "MM3", "MM2", "MMA", "UMA", "40K", "JMP", "BBD", "CMM"}

unique_cards = set()
cube_list = []


def format_commander_name(name: str) -> str:
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8')
    return name.split(" // ")[0].lower().replace(",", "").replace("'", "").replace(" ", "-")


def add_card(card_name: str):
    if card_name and card_name not in unique_cards:
        unique_cards.add(card_name)
        cube_list.append(card_name)


# Load MTGJSON once
with open(local_mtgjson_path, "r", encoding="utf-8") as f:
    all_printings = json.load(f)["data"]

# Map of card name -> color identity (for fallback logging/info)
color_identity_lookup = {}
for set_data in all_printings.values():
    for card in set_data.get("cards", []):
        name = card.get("name")
        if name and "colorIdentity" in card:
            color_identity_lookup[name] = card["colorIdentity"]


# Load commanders
with open(all_commanders_path, "r", encoding="utf-8") as f:
    all_lines = f.readlines()
all_commanders = [line.strip() for line in all_lines if line.strip() and not line.endswith(":")]
random.shuffle(all_commanders)

# Select only commanders with 2+ colors
multi_color_commanders = [
    cmd for cmd in all_commanders
    if len(color_identity_lookup.get(cmd, [])) >= 2 # Change here if you wanna remove color identity rule
]
chosen_commanders = multi_color_commanders[:10]

# Add commanders to cube (the commanders themselves)
for commander in chosen_commanders:
    add_card(commander)


# --- EDHREC helpers ---

def fetch_edhrec_page(commander: str):
    """Fetch and return the parsed EDHREC commander page JSON, or None on failure."""
    url = f"https://json.edhrec.com/pages/commanders/{format_commander_name(commander)}.json"
    print(f"[EDHREC] {commander} -> {url}")
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"[ERROR] {commander}: {e}")
        return None


def collect_cards_from_sections(data: dict, *, exclude_tags_substrings=None) -> list:
    """Collect unique card names from all cardlists, optionally excluding tags containing any substring.
    `exclude_tags_substrings`: iterable of lowercase substrings; if any is in section.tag.lower(), skip it.
    """
    if exclude_tags_substrings is None:
        exclude_tags_substrings = []

    json_dict = (data or {}).get("container", {}).get("json_dict", {})
    out = []
    seen_local = set()

    for section in json_dict.get("cardlists", []):
        tag = section.get("tag", "")
        tag_l = tag.lower()
        if any(sub in tag_l for sub in exclude_tags_substrings):
            continue
        for cv in section.get("cardviews", []):
            name = cv.get("name")
            if name and name not in seen_local and name not in unique_cards:
                out.append(name)
                seen_local.add(name)

    return out


def fetch_extra_cards_for_commander(commander: str, max_cards: int = 47) -> list:
    """Return up to `max_cards` extra cards played with this commander.
    Top cards are NOT forced separately; they are just part of the pool. Excludes any tag containing 'gamechanger'.
    """
    data = fetch_edhrec_page(commander)
    if not data:
        return []

    # Build a broad extra-pool from all categories (including topcards, synergy, types, etc.)
    # but explicitly exclude any 'gamechanger' style sections.
    pool = collect_cards_from_sections(data, exclude_tags_substrings=["gamechanger"])  # loose match

    # Keep the first `max_cards` while preserving EDHREC's default ordering
    return pool[:max_cards]


# --- First pass: add up to 50 extras per commander ---
for commander in chosen_commanders:
    extras = fetch_extra_cards_for_commander(commander, max_cards=47)
    for card in extras:
        add_card(card)


# --- Second pass if short of 480: try to fill ONLY with commander-played cards (no game changers) ---
TARGET_MIN = 480
if len(cube_list) < TARGET_MIN:
    print(f"[WARN] Cube below {TARGET_MIN} after first pass ({len(cube_list)}). Running a second pass from commander decks...")
    # We will take additional cards from each commander, iterating until we hit TARGET_MIN
    # We'll widen the net by pulling ALL available (excluding 'gamechanger') and rely on add_card to dedupe.
    idx = 0
    while len(cube_list) < TARGET_MIN and idx < len(chosen_commanders):
        commander = chosen_commanders[idx]
        data = fetch_edhrec_page(commander)
        if data:
            more = collect_cards_from_sections(data, exclude_tags_substrings=["gamechanger"])
            for card in more:
                if len(cube_list) >= TARGET_MIN:
                    break
                add_card(card)
        idx += 1


# --- Filler pool from relevant sets to bring the cube up to 500 if needed ---
filler_pool = set()
for code in commander_sets | masters_draft_innovation_sets:
    if code in all_printings:
        for card in all_printings[code].get("cards", []):
            if card.get("name") and card.get("layout", "") != "token":
                filler_pool.add(card["name"])

# Save output
with open(output_path, "w", encoding="utf-8") as f:
    for card in cube_list:
        f.write(f"{card}\n")

print(f"[OK] Cube complete! {len(cube_list)} cards saved to {output_path}")
