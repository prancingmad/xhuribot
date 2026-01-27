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
    full_path = os.path.join(BASE_DIR, JSON_DIR, file)
    with open(full_path, "w") as f:
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

def find_leaderboard(player_dict):
    first_place_spot = {}
    second_place_spot = {}
    third_place_spot = {}
    fourth_place_spot = {}
    fifth_place_spot = {}

    for p in player_dict:
        player_name = player_dict[p]["player_name"]
        player_score = (player_dict[p]["player_level"] * 100) + player_dict[p]["player_exp"]
        if not first_place_spot:
            first_place_spot["name"] = player_name
            first_place_spot["score"] = player_score
        elif player_score > first_place_spot["score"]:
            if fifth_place_spot:
                fifth_place_spot = dict(fourth_place_spot)
            if fourth_place_spot:
                fourth_place_spot = dict(third_place_spot)
            if third_place_spot:
                third_place_spot = dict(second_place_spot)
            if second_place_spot:
                second_place_spot = dict(first_place_spot)
            first_place_spot["name"] = player_name
            first_place_spot["score"] = player_score
        else:
            if not second_place_spot:
                second_place_spot["name"] = player_name
                second_place_spot["score"] = player_score
            elif player_score > second_place_spot["score"]:
                if fifth_place_spot:
                    fifth_place_spot = dict(fourth_place_spot)
                if fourth_place_spot:
                    fourth_place_spot = dict(third_place_spot)
                if third_place_spot:
                    third_place_spot = dict(second_place_spot)
                second_place_spot["name"] = player_name
                second_place_spot["score"] = player_score
            else:
                if not third_place_spot:
                    third_place_spot["name"] = player_name
                    third_place_spot["score"] = player_score
                elif player_score > third_place_spot["score"]:
                    if fifth_place_spot:
                        fifth_place_spot = dict(fourth_place_spot)
                    if fourth_place_spot:
                        fourth_place_spot = dict(third_place_spot)
                    third_place_spot["name"] = player_name
                    third_place_spot["score"] = player_score
                else:
                    if not fourth_place_spot:
                        fourth_place_spot["name"] = player_name
                        fourth_place_spot["score"] = player_score
                    elif player_score > fourth_place_spot["score"]:
                        if fifth_place_spot:
                            fifth_place_spot = dict(fourth_place_spot)
                        fourth_place_spot["name"] = player_name
                        fourth_place_spot["score"] = player_score
                    else:
                        if not fifth_place_spot:
                            fifth_place_spot["name"] = player_name
                            fifth_place_spot["score"] = player_score
                        elif player_score > fifth_place_spot["score"]:
                            fifth_place_spot["name"] = player_name
                            fifth_place_spot["score"] = player_score
                        else:
                            continue

    return first_place_spot, second_place_spot, third_place_spot, fourth_place_spot, fifth_place_spot