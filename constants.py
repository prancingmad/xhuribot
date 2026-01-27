import os

# File constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_DIR = "stored_info"

# Mod constants
MOD_ROLE = "Mod"
LOG_CHANNEL_NAME = "modbot_output"
BATTLE_CHANNEL = "battle_room"
BOT_CHANNEL = "bot-commands"

# Spare comment

# Combat game constants
conmath = 60
DAGGER_ATTACK_TIMER = 8 * conmath * conmath
SWORD_ATTACK_TIMER = 18 * conmath * conmath
MACE_ATTACK_TIMER = 24 * conmath * conmath
FIREBALL_ATTACK_TIMER = 48 * conmath * conmath
HEAL_TIMER =  18 * conmath * conmath
PUNCH_ATTACK_TIMER = 1 * conmath * conmath

EMOJI_TRIGGERS = {
    "xhuri": ("jellyxhuri", "🐲"),
    "jed": ("jellyjed", "🤠"),
    "jebediah": ("jellyjed", "🤠"),
    "cadril": ("cadrilgrump", "😡"),
    "amalthea": ("amalthealook", "🌙"),
    "serryn": ("serrynlfg2", "🌲"),
    "erendil": ("erendilsquint", "☕"),
    "beau": ("beauheart", "❤️"),
    "broom": ("🧹", "🧹")
}
