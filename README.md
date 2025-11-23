# XhuriBot — Community Discord Bot

XhuriBot is a custom-built Discord bot designed for moderation, community engagement, and a fun turn-based cooperative combat system where users team up to fight randomly chosen enemies from a list.

The bot includes moderation tools, social interaction commands, stream alert toggles, YouTube Shorts utilities, and a lite RPG-style combat system with leveling, cooldowns, and automated enemy attacks.

## Features

### Moderation Tools

- Auto-delete messages containing banned words based off the banned_words.json
- Auto-log deleted messages to the designated log_channel so Moderators can review
- `!addbannedword <word>` — Add a banned word
- `!removebannedword <word>` — Remove a banned word
- `!listbannedwords` — Show all banned words
- `!modcommands` — List moderator commands
- `!addshort <url>` — Add a short
- `!removeshort <url>` — Remove a short

### User Utilities

- `/roll1d20` — Roll a d20
- `/hixhuri` — Personalized greeting
- `/randomshort` — Post a random YouTube Short (with optional flavor text)
- `/modrequest` — Users can request moderator help

Users can toggle special alert roles for when some of the creators are streaming:
- `/toggletwigalerts`
- `/toggleolliealerts`

## Cooldowns & Combat Mechanics

### RPG Combat System

- `/join_the_fight` — Add yourself as a player
- `/leavethefight` — Remove yourself and reset your progress- 
- `/summonenemy` — Spawn a random enemy (mods can spawn bosses)
- `/attack` — Attack with weapons that deal different damage and have cooldowns
- `/heal` — Heal the party
- Automated hourly enemy attacks
- Party-wide EXP distribution and leveling
- Scaling enemies that grow stronger after each defeat
- All combat data stored in JSON files

### Weapon Damage

| Weapon | Damage Formula | Cooldown |
|--------|----------------|----------|
| Dagger | level × 1 | Short |
| Sword | level × 1.5 | Medium |
| Mace | level × 2 | Long |
| Fireball | level × 4 | Very long |

### Enemy Scaling

- Regular enemies: +20% HP and +0.5 damage per defeat
- Bosses: +50% HP and +1 damage per defeat

## Project Structure Overview

```
├── README.md
├── constants.py
├── main.py
├── reuse_functions.py
└── stored_info
    ├── banned_words.json
    ├── bosses.json
    ├── current_enemy.json
    ├── enemies.json
    ├── hello_responses.json
    ├── players.json
    ├── random_shorts.json
    └── short_comments.json
```

## Requirements

- Python 3.10+
- discord.py (2.0+)
- python-dotenv
- asyncio
- Bot permissions for message deletion, embeds, and managing roles

Install dependencies:

```
pip install discord.py python-dotenv
```

## Running the Bot

Create a `.env` file:

```
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN_HERE
```

Start the bot:

```
python bot.py
```

Slash commands will sync automatically when the bot starts.

## Key JSON Files

| File | Purpose |
|------|---------|
| `players.json` | Stores player stats, EXP, cooldowns |
| `current_enemy.json` | Stores the active enemy |
| `enemies.json`, `bosses.json` | Lists of enemies |
| `party_health.json` | Shared party HP |
| `banned_words.json` | Moderation word filter |
| `shorts.json` | Stored YouTube Shorts |
| `short_comments.json` | Flavor text for `/randomshort` |

## Notes

- Certain features require channel names to match those in `constants.py` (e.g., `battle_room`, `log_channel`).
- Moderation commands (commands prefixed with !) require the role defined as `MOD_ROLE`.
