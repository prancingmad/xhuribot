import os
import json
import asyncio
import discord

from constants import BASE_DIR, JSON_DIR, MOD_ROLE

background_task = None

def load_json(file):
    with open(os.path.join(BASE_DIR, JSON_DIR, file)) as json_file:
        return json.load(json_file)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def is_valid_short_url(url: str):
    return url.startswith("https://www.youtube.com/shorts/")

def highlight_word(text, target):
    return text.replace(
        target, f"**{target.upper()}**"
    )

async def start_timer(minutes, callback):
    await asyncio.sleep(minutes * 60)
    await callback()

async def react_with_emoji(message, custom_name, fallback):
    emoji = discord.utils.get(message.guild.emojis, name=custom_name)
    try:
        await message.add_reaction(str(emoji) if emoji else fallback)
    except discord.HTTPEXception as e:
        print(f"Failed to add reaction: {e}")