import os

# File constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_DIR = "stored_info"
BANNED_WORDS_FILE = "banned_words.json"
BOSSES_FILE = "bosses.json"
CURRENT_ENEMY = "current_enemy.json"
ENEMIES_FILE = "enemies.json"
HELLO_RESPONSES_FILE = "hello_responses.json"
PLAYERS_FILE = "players.json"
RANDOM_SHORTS_FILE = "random_shorts.json"
SHORT_COMMENTS_FILE = "short_comments.json"
PARTY_HEALTH_FILE = "party_health.json"

# Mod constants
MOD_ROLE = "Mod"
LOG_CHANNEL_NAME = "modbot_output"
BATTLE_CHANNEL = "battle_room"

# Spare comment

# Combat game constants
conmath = 60
DAGGER_ATTACK_TIMER = 8 * conmath * conmath
SWORD_ATTACK_TIMER = 18 * conmath * conmath
MACE_ATTACK_TIMER = 24 * conmath * conmath
FIREBALL_ATTACK_TIMER = 48 * conmath * conmath
HEAL_TIMER =  18 * conmath * conmath

EMOJI_TRIGGERS = {
    "xhuri": ("jellyxhuri", "🐲"),
    "jed": ("jellyjed", "🤠"),
    "jebediah": ("jellyjed", "🤠"),
    "cadril": ("cadrilgrump", "😡"),
    "amalthea": ("amalthealook", "🌙"),
    "serryn": ("serrynlfg2", "🌲"),
    "erendil": ("erendilsquint", "☕"),
    "beau": ("beauheart", "❤️")
}