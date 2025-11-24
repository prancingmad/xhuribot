import logging
import random
import re
import math
import time
import asyncio
import os
import discord

from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from typing import Optional
from constants import *
from reuse_functions import *

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

file_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    level=logging.DEBUG,
    format = '%(asctime)s:%(levelname)s:%(name)s: %(message)s',
    handlers = [
        logging.FileHandler('discord.log', encoding='utf-8', mode='w')
    ]
)

bot = commands.Bot(command_prefix='!', intents=intents)
enemy_attacking = False

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    global enemy_attacking

    enemy = load_json(CURRENT_ENEMY)

    if enemy and not enemy_attacking:
        enemy_attacking = True
        asyncio.create_task(hourly_enemy_check())

    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

banned_words = set(load_json(BANNED_WORDS_FILE))
hello_responses = (load_json(HELLO_RESPONSES_FILE))
shorts = (load_json(RANDOM_SHORTS_FILE))
short_comments = load_json(SHORT_COMMENTS_FILE)

async def hourly_enemy_check():
    global enemy_attacking
    while enemy_attacking:
        await asyncio.sleep(60 * 60)

        enemy = load_json(CURRENT_ENEMY)
        if not enemy_attacking or not enemy:
            break

        health = load_json(PARTY_HEALTH_FILE)
        damage = math.floor(enemy["damage"])
        new_health = [health[0] - damage]
        battle_room = discord.utils.get(bot.get_all_channels(), name=BATTLE_CHANNEL)

        if new_health[0] <= 0:
            await battle_room.send("The enemy has defeated the party...")
            save_json(CURRENT_ENEMY, {})
            players = load_json(PLAYERS_FILE)
            for victor_id, victor in players.items():
                if victor.get("contributed"):
                    victor["contributed"] = False
            save_json(PLAYERS_FILE, players)
            save_json(PARTY_HEALTH_FILE, [])
            enemy_attacking = False
        else:
            await battle_room.send(f"The enemy has attacked the party, and dealt {damage} damage - Party's Current Health: {new_health[0]}")
            save_json(PARTY_HEALTH_FILE, new_health)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    lower_msg = message.content.lower()
    triggering_word = None

    for keyword, (custom, fallback) in EMOJI_TRIGGERS.items():
        if keyword in lower_msg:
            await react_with_emoji(message, custom, fallback)

    for word in banned_words:
        if re.search(rf'\b{re.escape(word)}\b', lower_msg):
            triggering_word = word
            break

    if triggering_word:
        try:
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, your message was removed for inappropriate language.",
                delete_after=5
            )
            await log_deleted_message(message, triggering_word)
        except discord.Forbidden:
            print("Missing permission to delete or send messages.")
        except discord.HTTPException as e:
            print(f"Failed to delete or log message: {e}")

    await bot.process_commands(message)

async def log_deleted_message(message, word):
    log_channel = discord.utils.get(message.guild.text_channels, name=LOG_CHANNEL_NAME)

    if log_channel is None:
        print (f"Log channel #{LOG_CHANNEL_NAME} not found.")
        return

    if not isinstance(log_channel, discord.TextChannel):
        print(f" log_channel is not a TextChannel: {type(log_channel)}")
        return

    highlighted_msg = highlight_word(message.content, word)

    embed = discord.Embed(
        title="Message Deleted",
        color=discord.Color.red(),
        timestamp=message.created_at
    )
    embed.add_field(name="User", value=message.author.mention, inline=True)
    embed.add_field(name="Channel", value=message.channel.mention, inline=True)
    embed.add_field(name="Triggered Word", value=f"'{word}'", inline = False)
    embed.add_field(name="Message", value=highlighted_msg[:1024], inline=False)


    await log_channel.send(embed=embed)

@bot.command(name="addbannedword")
@commands.has_role(MOD_ROLE)
async def addbannedword(ctx, word: str):
    word = word.lower()

    if word in banned_words:
        await ctx.send("That word is already on the ban list. If you'd like to see all currently banned words, please run !listbannedwords.")
    else:
        banned_words.add(word)
        save_json(BANNED_WORDS_FILE, list(banned_words))
        await ctx.send(f"Added '{word}' to the banned words list. If you'd like to see all currently banned words, please run !listbannedwords.")

@bot.command(name="removebannedword")
@commands.has_role(MOD_ROLE)
async def removebannedword(ctx, word: str):
    word = word.lower()

    if word in banned_words:
        banned_words.remove(word)
        save_json(BANNED_WORDS_FILE, list(banned_words))
        await ctx.send(f"Removed '{word}' from the banned words list. If you'd like to see all currently banned words, please run !listbannedwords.")
    else:
        await ctx.send(f"'{word}' is not currently banned. If you'd like to see all currently banned words, please run !listbannedwords.")

@bot.command(name="listbannedwords")
@commands.has_role(MOD_ROLE)
async def listbannedwords(ctx):
    if banned_words:
        word_list = ", ".join(sorted(banned_words))
        await ctx.send(f"**Banned Words:**\n{word_list}")
    else:
        await ctx.send("The banned words list is currently empty, or not loading properly.")

@bot.command(name="addshort")
@commands.has_role(MOD_ROLE)
async def addshort(ctx, url: str):
    if "youtube.com/shorts" not in url:
        await ctx.send("That doesn't look like a valid YouTube Shorts link. Please check the link, and try again!")
        return

    if url in shorts:
        await ctx.send("That video is already in the list.")
        return

    shorts.append(url)
    save_json(RANDOM_SHORTS_FILE, shorts)
    await ctx.send("Short added!")

@bot.command(name="removeshort")
@commands.has_role(MOD_ROLE)
async def removeshort(ctx, url: str):
    url = url.strip()

    if url in shorts:
        shorts.remove(url)
        save_json(RANDOM_SHORTS_FILE, shorts)
        await ctx.send("Short removed!")
    else:
        await ctx.send("That video is not in the list.")

@bot.command(name="clearenemy")
@commands.has_role(MOD_ROLE)
async def clearenemy(ctx):
    if not os.path.exists(CURRENT_ENEMY):
        await ctx.send("There is no enemy currently active.")
        return

    try:
        os.remove(CURRENT_ENEMY)
    except Exception as e:
        await ctx.send (f"Failed to clear enemy: {e}")
        return

    players = load_json(PLAYERS_FILE)
    for player in players.values():
        player["contributed"] = False
    save_json(PLAYERS_FILE, players)

    await ctx.send("The enemy has retreated, for now!")

@bot.command(name="modcommands")
@commands.has_role(MOD_ROLE)
async def modcommands(ctx):
    mod_command_list = [
        "`!addbannedword <word>` – Adds a word to the banned list",
        "`!removebannedword <word>` – Removes a word from the banned list",
        "`!listbannedwords` – View all banned words",
        "`!addshort <url>` - Adds a short to the Youtube Shorts list",
        "`!removeshort <url>` – Removes a short from the Youtube Shorts list",
        "`!modcommands` – Show this list of mod-only commands",
        "`!clearenemy` - Clears out the current enemy"
    ]

    response = "**Mod-Only Commands:**\n" + "\n".join(mod_command_list)
    await ctx.send(response)

@bot.tree.command(name="roll1d20", description="Roll a random number from 1 to 20")
async def roll1d20(interaction: discord.Interaction):
    result = random.randint(1, 20)
    user_mention = interaction.user.mention
    await interaction.response.send_message(f"{user_mention} rolled a **{result}**!")

@bot.tree.command(name="hixhuri", description="Say hello to everyone's favorite Kobold!")
async def hi_xhuri(interaction: discord.Interaction):
    response = random.choice(hello_responses)
    personalized = response.format(user=interaction.user.display_name)
    await interaction.response.send_message(personalized)

@bot.tree.command(name="toggletwigalerts", description="Add or remove the role to be alerted with Twig is streaming!")
async def toggle_twig_alerts(interaction: discord.Interaction):
    guild = interaction.guild
    member = interaction.user
    role_name = "twig_stream_alert"
    role = discord.utils.get(guild.roles, name=role_name)

    if not role:
        await interaction.response.send_message(f"The role '{role_name}' does not exist on this server, or there has been an error. Please alert a mod!", ephemeral=True)
        return

    if role in member.roles:
        await member.remove_roles(role)
        await interaction.response.send_message(f"Removed Twig stream alerts. You will no longer be notified when Twig is streaming.", ephemeral=True)
    else:
        await member.add_roles(role)
        await interaction.response.send_message(f"Added Twig stream alerts. You will be notified when Twig is streaming!", ephemeral=True)

@bot.tree.command(name="toggleolliealerts", description="Add or remove the role to be alerted with Ollie is streaming!")
async def toggle_ollie_alerts(interaction: discord.Interaction):
    guild = interaction.guild
    member = interaction.user
    role_name = "ollie_stream_alert"
    role = discord.utils.get(guild.roles, name=role_name)

    if not role:
        await interaction.response.send_message(f"The role '{role_name}' does not exist on this server, or there has been an error. Please alert a mod!", ephemeral=True)
        return

    if role in member.roles:
        await member.remove_roles(role)
        await interaction.response.send_message(f"Removed Ollie stream alerts. You will no longer be notified when Ollie is streaming.", ephemeral=True)
    else:
        await member.add_roles(role)
        await interaction.response.send_message(f"Added Ollie stream alerts. You will be notified when Ollie is streaming!", ephemeral=True)

@bot.tree.command(name="randomshort", description="Displays a random Vibe Check YouTube short to the channel!")
async def random_short(interaction: discord.Interaction):
    try:
        if not shorts:
            await interaction.response.send_message("No Shorts available, or an error retrieving them - please alert a mod!")
            return
    except Exception as e:
        await interaction.response.send_message("Something went wrong while trying to fetch a short.")
        print(f"Error in randomshort: {e}")
        return

    valid_short = None
    shuffled_shorts = shorts[:]
    random.shuffle(shuffled_shorts)
    mod_channel = discord.utils.get(interaction.guild.text_channels, name=LOG_CHANNEL_NAME)

    for url in shuffled_shorts:
        clean_url = url.strip()
        if is_valid_short_url(clean_url):
            valid_short = clean_url
            break
        else:
            print(f"Invalid short: '{clean_url}'")
            if mod_channel:
                await mod_channel.send(f"Detected bad short link in list: '{clean_url}'")

    if not valid_short:
        await interaction.response.send_message("All shorts appear to be invalid, or an error retrieving them - please alert a mod!")
        return

    comment = random.choice(short_comments) if short_comments else ""
    message = f"{comment}\n{valid_short}" if comment else valid_short

    await interaction.response.send_message(message)

@bot.tree.command(name="modrequest", description=f"Sends a message to the moderator team to DM you and follow up regarding an issue.")
@app_commands.describe(message="Please give a brief summary of your request")
async def mod_request(interaction: discord.Interaction, message:str):
    guild = interaction.guild
    channel = discord.utils.get(guild.text_channels, name=LOG_CHANNEL_NAME)
    mod = discord.utils.get(guild.roles, name=MOD_ROLE)

    if channel is None or mod is None:
        await interaction.response.send_message(
            "Could not find the log channel or moderator role. Please check the configuration.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="Mod Assistance Request",
        description=f"{interaction.user.mention} is requesting assistance from {mod.mention}!",
        color=discord.Color.red()
    )
    embed.add_field(name="Message", value=message, inline=False)
    embed.set_footer(text=f"User ID: {interaction.user.id}")
    embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)

    await channel.send(content=f"{mod.mention}", embed=embed)

    await interaction.response.send_message(f"I have sent your request to the moderating team. The first available mod will reach out to you as quickly as they can, please have your DMs open!", ephemeral=True)

@bot.tree.command(name="jointhefight", description="Add yourself to the player list and join the fight!")
async def join_the_fight(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    players = load_json(PLAYERS_FILE)

    if user_id in players:
        await interaction.response.send_message("You've already joined the fight!", ephemeral=True)
        return

    players[user_id] = {
        "player_name": interaction.user.display_name,
        "player_level": 1,
        "player_exp": 0,
        "contributed": False,
        "cooldowns": {}
    }
    save_json(PLAYERS_FILE, players)
    await interaction.response.send_message("You've joined the fight! Use /summonenemy or /attack in #battle_room!", ephemeral=True)

@bot.tree.command(name="leavethefight", description="Remove yourself from the player list. Rejoining later resets you to level 1.")
async def leave_the_fight(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    players = load_json(PLAYERS_FILE)

    if user_id in players:
        del players[user_id]
        save_json(PLAYERS_FILE, players)
        await interaction.response.send_message("You have been removed from the players list, and are eligible to rejoin in the future if you wish!", ephemeral=True)
    else:
        await interaction.response.send_message("You are not currently on the player's list.", ephemeral=True)

@bot.tree.command(name="summonenemy", description="Summon a random enemy for the community to fight!")
async def summon_enemy(interaction: discord.Interaction):
    battle_room = discord.utils.get(interaction.guild.text_channels, name=BATTLE_CHANNEL)
    global enemy_attacking

    if interaction.channel != battle_room:
        await interaction.response.send_message(f"This command can only be used in the #{BATTLE_CHANNEL} channel.", ephemeral=True)
        return

    await interaction.response.defer()

    enemy_data = load_json(CURRENT_ENEMY)
    if enemy_data:
        await interaction.response.send_message("An enemy is already present! Work with the community to defeat it first!", ephemeral=True)
        return

    is_mod = any(role.name == MOD_ROLE for role in interaction.user.roles)
    source_file = "bosses.json" if is_mod else "enemies.json"
    enemies = load_json(source_file)

    if not enemies:
        await interaction.response.send_message("No enemies found in the file, or an error has occurred. Please inform a mod!", ephemeral=True)
        return

    enemy = random.choice(enemies)
    enemy_name = enemy["enemy_name"]
    image_path = enemy.get("image_path")

    current_enemy = {
        "enemy_name": enemy_name,
        "enemy_health": enemy["enemy_health"],
        "enemy_exp": enemy["enemy_exp"],
        "damage": enemy["damage"],
        "message_id": None,
        "channel_id": interaction.channel.id,
        "source_file": source_file
    }

    embed = discord.Embed(
        title=f"{enemy_name} Appears!",
        description=(
            f"🩸 **Health:** {enemy['enemy_health']}\n"
            f"🏆 **EXP REWARD:** {enemy['enemy_exp']}\n"
            f"💖 **Party Health:** 10"
        ),
        color=discord.Color.red()
    )

    file = None
    if image_path and os.path.exists(image_path):
        file = discord.File(image_path, filename="enemy.png")
        embed.set_image(url="attachment://enemy.png")

    if file:
        message = await interaction.channel.send(embed=embed, file=file)
    else:
        message = await interaction.channel.send(embed=embed)

    current_enemy["message_id"] = message.id
    party_health = [10]
    save_json(CURRENT_ENEMY, current_enemy)
    save_json(PARTY_HEALTH_FILE, party_health)
    enemy_attacking = True
    asyncio.create_task(hourly_enemy_check())

    await interaction.followup.send(f"{interaction.user.mention} encountered a **{enemy['enemy_name']}**! Work together to defeat it!")

@bot.tree.command(name="attack", description="Attack the current enemy!")
@app_commands.describe(weapon="Choose your attack!")
@app_commands.choices(weapon=[
    app_commands.Choice(name="Dagger", value="Dagger"),
    app_commands.Choice(name="Sword", value="Sword"),
    app_commands.Choice(name="Mace", value="Mace"),
    app_commands.Choice(name="Fireball", value="Fireball")
])
async def attack(interaction: discord.Interaction, weapon: Optional[app_commands.Choice[str]] = None):
    battle_room = discord.utils.get(interaction.guild.text_channels, name=BATTLE_CHANNEL)
    if interaction.channel != battle_room:
        await interaction.response.send_message(f"This command can only be used in the #{BATTLE_CHANNEL} channel.", ephemeral=True)
        return

    enemy = load_json(CURRENT_ENEMY)
    if not enemy:
        await interaction.response.send_message("There's currently no enemy to attack, use /summon_enemy first!", ephemeral=True)
        return

    players = load_json(PLAYERS_FILE)
    user_id = str(interaction.user.id)
    if user_id not in players:
        await interaction.response.send_message("You should /join_the_fight first!", ephemeral=True)
        return

    player = players[user_id]
    now = time.time()
    player["cooldowns"] = player.get("cooldowns", {})
    attack_cd = player["cooldowns"].get("attack", 0)
    damage = 0

    if now < attack_cd:
        remaining = int(attack_cd - now)
        hours, rem = divmod(remaining, 3600)
        minutes, seconds = divmod(rem, 60)
        time_str = f"{hours:02}:{minutes:02}:{seconds:02}"

        await interaction.response.send_message(
            f"You must wait **{time_str}** before attacking again!", ephemeral=True
        )
        return

    weapon = weapon.value if weapon else "Sword"
    if weapon == "Dagger":
        damage = player["player_level"]
        player["cooldowns"]["attack"] = now + DAGGER_ATTACK_TIMER
    elif weapon == "Sword":
        damage = math.ceil(player["player_level"] * 1.5)
        player["cooldowns"]["attack"] = now + SWORD_ATTACK_TIMER
    elif weapon == "Mace":
        damage = player["player_level"] * 2
        player["cooldowns"]["attack"] = now + MACE_ATTACK_TIMER
    elif weapon == "Fireball":
        damage = player["player_level"] * 4
        player["cooldowns"]["attack"] = now + FIREBALL_ATTACK_TIMER

    enemy["enemy_health"] -= damage

    if not player["contributed"]:
        player["contributed"] = True

    if enemy["enemy_health"] > 0:
        save_json(CURRENT_ENEMY, enemy)
        save_json(PLAYERS_FILE, players)
        await interaction.response.send_message(
            f"🗡️ {interaction.user.mention} attacked with their {weapon}, and dealt **{damage}** damage to **{enemy['enemy_name']}**!\n"
            f"💔 Remaining HP: {enemy['enemy_health']}",
            ephemeral=False
        )
        return

    final_blow_msg = (
        f"{interaction.user.mention} attacked with their {weapon}, dealt **{damage}** damage, and defeated **{enemy['enemy_name']}**!\n"
        f"All attackers gained **{enemy['enemy_exp']} EXP**!"
        f"{enemy['enemy_name']} will return in the future, stronger!"
    )

    exp_reward = enemy["enemy_exp"]
    source_file = enemy.get("source_file")

    level_ups = []
    for victor_id, victor in players.items():
        if victor.get("contributed"):
            victor["contributed"] = False
            victor["player_exp"] += exp_reward

            while victor["player_exp"] >= 100:
                level_ups.append(victor["player_name"])
                victor["player_exp"] -= 100
                victor["player_level"] += 1
    party_health = []
    save_json(PLAYERS_FILE, players)
    save_json(PARTY_HEALTH_FILE, party_health)
    global enemy_attacking
    enemy_attacking = False

    if source_file:
        enemy_list = load_json(source_file)
        for e in enemy_list:
            if e["enemy_name"] == enemy["enemy_name"]:
                if source_file == "enemies.json":
                    e["enemy_health"] = math.ceil(e["enemy_health"] * 1.1)
                    e["damage"] += 0.5
                    e["enemy_exp"] += 1
                elif source_file == "bosses.json":
                    e["enemy_health"] = math.ceil(e["enemy_health"] * 1.2)
                    e["damage"] += 1
                    e["enemy_exp"] += 10
                break
        save_json(source_file, enemy_list)
        save_json(CURRENT_ENEMY, {})

    if level_ups:
        final_blow_msg += "\n\n**Level Up!**\n" + "\n".join(f"⭐ {name} leveled up!" for name in level_ups)

    await interaction.response.send_message(final_blow_msg, ephemeral=False)

@bot.tree.command(name="heal", description="Heals the party!")
async def heal(interaction: discord.Interaction):
    battle_room = discord.utils.get(interaction.guild.text_channels, name=BATTLE_CHANNEL)
    if interaction.channel != battle_room:
        await interaction.response.send_message(f"This command can only be used in the #{BATTLE_CHANNEL} channel.",
                                                ephemeral=True)
        return

    enemy = load_json(CURRENT_ENEMY)
    if not enemy:
        await interaction.response.send_message("There's currently no enemy attacking the party, use /summon_enemy first!",
                                                ephemeral=True)
        return

    players = load_json(PLAYERS_FILE)
    user_id = str(interaction.user.id)
    if user_id not in players:
        await interaction.response.send_message("You should /join_the_fight first!", ephemeral=True)
        return

    player = players[user_id]
    now = time.time()

    heal_cd = player["cooldowns"].get("attack", 0)

    if now < heal_cd:
        remaining = int(heal_cd - now)
        hours, rem = divmod(remaining, 3600)
        minutes, seconds = divmod(rem, 60)
        time_str = f"{hours:02}:{minutes:02}:{seconds:02}"

        await interaction.response.send_message(
            f"You must wait **{time_str}** before doing an action!", ephemeral=True
        )
        return
    player["cooldowns"]["attack"] = now + HEAL_TIMER
    health = load_json(PARTY_HEALTH_FILE)
    new_health = [health[0] + player["player_level"]]
    await interaction.response.send_message(
        f"❤️ {interaction.user.mention} has healed the party for {player['player_level']}, bringing the party to {new_health[0]}!",
        ephemeral=False
    )
    player["contributed"] = True
    save_json(PLAYERS_FILE, players)
    save_json(PARTY_HEALTH_FILE, new_health)


@bot.tree.command(name="checkstats", description="Checks your current stats.")
async def checkstats(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    players = load_json(PLAYERS_FILE)

    if user_id not in players:
        await interaction.response.send_message("You should /join_the_fight first!", ephemeral=True)
        return

    player = players[user_id]
    p_name = player["player_name"]
    p_level = player["player_level"]
    p_exp = player["player_exp"]

    now = time.time()
    attack_cd = player["cooldowns"].get("attack", 0)

    if now < attack_cd:
        remaining = int(attack_cd - now)
        hours, rem = divmod(remaining, 3600)
        minutes, seconds = divmod(rem, 60)
        time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
        p_attack = f"must wait **{time_str}** before attacking again!"
    else:
        p_attack = "are able to attack!"

    await interaction.response.send_message(
        f"Greetings {p_name}! You are currently level {p_level}, with {p_exp} exp, and you {p_attack}",
        ephemeral=True)

print("Starting Xhuribot...")
bot.run(token)