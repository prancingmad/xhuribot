import json
import shutil
from pathlib import Path

# File locations
PLAYERS_FILE = Path("stored_info/players.json")
BACKUP_FILE = Path("stored_info/players.json.backup")

def main():
    if not PLAYERS_FILE.exists():
        print(f"Error: Could not find {PLAYERS_FILE}")
        return

    # Create a backup before making changes
    shutil.copy2(PLAYERS_FILE, BACKUP_FILE)
    print(f"Backup created: {BACKUP_FILE}")

    # Load player data
    with PLAYERS_FILE.open("r", encoding="utf-8") as file:
        players = json.load(file)

    updated_count = 0

    for player_id, player in players.items():
        old_level = player["player_level"]
        old_exp = player["player_exp"]

        # Convert current level and experience into total experience
        total_exp = (old_level * 100) + old_exp

        # Start with a level-up requirement of 100
        player_to_level = 100
        player["player_exp"] = total_exp

        # Process level-ups
        while player["player_exp"] >= player_to_level:
            player["player_exp"] -= player_to_level
            player["player_level"] += 1
            player_to_level += 10

        # Save the next level-up requirement
        player["player_to_level"] = player_to_level

        updated_count += 1

        print(
            f"{player['player_name']}: "
            f"Level {old_level} -> {player['player_level']}, "
            f"EXP {old_exp} -> {player['player_exp']}, "
            f"Next level requires {player_to_level} EXP"
        )

    # Save updated player data
    with PLAYERS_FILE.open("w", encoding="utf-8") as file:
        json.dump(players, file, indent=4)
        file.write("\n")

    print(f"\nFinished! Updated {updated_count} players.")

if __name__ == "__main__":
    main()