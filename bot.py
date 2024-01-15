import time
import discord
from discord.ext import commands
from discord.ui import Select, View
import os
import requests
from datetime import datetime, timedelta

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix='$db', help_command=None, intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}!")
    amt = 0
    for guild in bot.guilds:
        amt = amt + 1
    await bot.change_presence(activity=discord.Game(name=f"🎮Discblox | {amt}"))
    try:
        synced = await bot.tree.sync()
        print("Loaded commands")
    except Exception as e:
        print(e)


def get_user_id(username):
    url = "https://users.roblox.com/v1/usernames/users"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {
        "usernames": [username],
        "excludeBannedUsers": True
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        user_data = response.json()
        user_id = user_data["data"][0]["id"] if "data" in user_data and user_data["data"] else None
        return user_id
    except requests.RequestException as e:
        print(f"Failed to get user ID for {username}: {e}")
        return None


def get_user_outfits(user_id):
    url = f"https://avatar.roblox.com/v1/users/{user_id}/outfits"
    params = {
        "outfitType": "Avatar",
        "page": 1,
        "itemsPerPage": 25
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        outfits_data = response.json()
        return outfits_data.get("data", [])

    except requests.RequestException as e:
        print(f"Failed to retrieve user outfits: {e}")
        return []


@bot.tree.command(name="usertoid", description="Get a user id from a username for roblox.")
async def pinfo(interaction: discord.Interaction, username: str):
    embed = discord.Embed(title=f"User ({username})", color=0x6495ED)
    user_id = get_user_id(username)
    if user_id:
        embed.add_field(name="Username", value=username, inline=True)
        embed.add_field(name="UserID", value=user_id, inline=True)
    else:
        embed.add_field(name="Username", value=username, inline=True)
        embed.add_field(name="UserID", value="Failed to retrive user id", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help", description="Brings up the help menu.")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title="Help", description=f"{bot.user.name} is a multi-purpose bot with various commands.",
                          color=0x6495ED)
    embed.add_field(name=":shield: help", value="View Commands (Removed next update)", inline=True)
    embed.add_field(name=":shield: info", value="View bot info (Removed next update)", inline=True)
    embed.add_field(name=":shield: info-new", value="View bot info including commands", inline=True)
    embed.add_field(name="pinfo", value="Get player info", inline=True)
    embed.add_field(name="usertoid", value="Convert a username", inline=True)
    embed.add_field(name="outfit", value="Outfit data from id", inline=True)
    embed.add_field(name="listoutfits", value="(Gold) Get a user's outfits", inline=True)
    embed.add_field(name="gameinfo", value="View the info of a game", inline=True)
    embed.add_field(name="link", value="Link your account", inline=True)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="pinfo", description="Info of a roblox player.")
async def pinfo(interaction: discord.Interaction, userid: str):
    embed = discord.Embed(title=f"Player Info ({userid})", color=0x6495ED)
    try:
        response = requests.get(f"https://users.roblox.com/v1/users/{userid}")
        response.raise_for_status()
        user_data = response.json()
        username = user_data.get("name", "Username not found")
        displayName = user_data.get("displayName", "displayName not found")
        isBanned = user_data.get("isBanned", "isBanned not found")
        hasVerifiedBadge = user_data.get("hasVerifiedBadge", "hasVerifiedBadge not found")
        created = user_data.get("created", "created not found")
        description = user_data.get("description", "description not found")
        embed.add_field(name="Username", value=username, inline=True)
        embed.add_field(name="DisplayName", value=displayName, inline=True)
        embed.add_field(name="Banned", value=isBanned, inline=True)
        embed.add_field(name="Verified", value=hasVerifiedBadge, inline=True)
        embed.add_field(name="CreationDate", value=created, inline=True)
        embed.add_field(name="Description", value=description, inline=True)
    except requests.RequestException as e:
        embed.add_field(name="Error", value=f"Failed to fetch player info: {e}", inline=False)
    try:
        response = requests.get(f"https://inventory.roblox.com/v1/users/{userid}/can-view-inventory")
        response.raise_for_status()
        user_data = response.json()
        canView = user_data.get("canView", "canView not found")
        embed.add_field(name="ViewInventory", value=canView, inline=True)
    except requests.RequestException as e:
        embed.add_field(name="Error", value=f"Failed to fetch player info: {e}", inline=False)
    try:
        response = requests.get(f"https://friends.roblox.com/v1/users/{userid}/followers/count")
        response.raise_for_status()
        user_data = response.json()
        count = user_data.get("count", "count not found")
        embed.add_field(name="Followers", value=count, inline=True)
    except requests.RequestException as e:
        embed.add_field(name="Error", value=f"Failed to fetch player info: {e}", inline=False)
    try:
        response = requests.get(f"https://friends.roblox.com/v1/users/{userid}/followings/count")
        response.raise_for_status()
        user_data = response.json()
        count = user_data.get("count", "count not found")
        embed.add_field(name="Following", value=count, inline=True)
    except requests.RequestException as e:
        embed.add_field(name="Error", value=f"Failed to fetch player info: {e}", inline=False)
    try:
        response = requests.get(f"https://friends.roblox.com/v1/users/{userid}/friends/count")
        response.raise_for_status()
        user_data = response.json()
        count = user_data.get("count", "count not found")
        embed.add_field(name="Friends", value=count, inline=True)
    except requests.RequestException as e:
        embed.add_field(name="Error", value=f"Failed to fetch player info: {e}", inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="groupinfo", description="Info of a roblox group.")
async def groupinfo(interaction: discord.Interaction, groupid: str):
    embed = discord.Embed(title=f"Group Info ({groupid})", color=0x6495ED)
    try:
        response = requests.get(f"https://groups.roblox.com/v1/groups/{groupid}")
        response.raise_for_status()
        group_data = response.json()
        name = group_data.get("name", "name not found")
        description = group_data.get("description", "description not found")
        username = group_data["owner"].get("username", "username not found")
        displayname = group_data["owner"].get("displayName", "displayName not found")
        shout = group_data["shout"].get("body", "body not found")
        shoutposter = group_data["shout"]["poster"].get("username", "username not found")
        memberCount = group_data.get("memberCount", "memberCount not found")
        hasVerifiedBadge = group_data.get("hasVerifiedBadge", "hasVerifiedBadge not found")
        embed.add_field(name="Name", value=name, inline=True)
        embed.add_field(name="Description", value=description, inline=True)
        embed.add_field(name="Owner", value=f"{displayname} @{username}", inline=True)
        embed.add_field(name="Verified", value=hasVerifiedBadge, inline=True)
        embed.add_field(name="Shout", value=shout, inline=True)
        embed.add_field(name="ShoutPoster", value=shoutposter, inline=True)
        embed.add_field(name="Members", value=memberCount, inline=True)
        embed.add_field(name="Verified", value=hasVerifiedBadge, inline=True)
    except requests.RequestException as e:
        embed.add_field(name="Error", value=f"Failed to fetch player info: {e}", inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="listoutfits", description="(GOLD) Get a list of a roblox player's outfits.")
async def pinfo(interaction: discord.Interaction, userid: str):
    with open("gold.txt", "a+") as file:
        file.seek(0)
        lines = file.readlines()
        user_id = str(interaction.user.id)
        if any(user_id in line for line in lines):
            embed = discord.Embed(title=f"Outfit ({userid})", color=0x6495ED)
            outfits = get_user_outfits(userid)
            if outfits:
                for outfit in outfits:
                    outfit_id = outfit.get("id")
                    outfit_name = outfit.get("name")
                    embed.add_field(name=f"Name: {outfit_name}", value=f"ID: {outfit_id}")
            else:
                embed.add_field(name=f"Failed to retrieve outfits for user {user_id}")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("You do not own Gold! Do /gold for more information")


@bot.tree.command(name="outfit", description="Get a roblox outfit.")
async def pinfo(interaction: discord.Interaction, outfitid: str):
    embed = discord.Embed(title=f"Outfit ({outfitid})", color=0x6495ED)
    try:
        response = requests.get(
            f"https://thumbnails.roblox.com/v1/users/outfits?userOutfitIds={outfitid}&size=420x420&format=Png&isCircular=false")
        response.raise_for_status()
        outfit_data = response.json()
        image_url = outfit_data["data"][0]["imageUrl"]
        embed.set_image(url=image_url)
    except requests.RequestException as e:
        embed.add_field(name="Error", value=f"Failed to fetch player info: {e}", inline=False)
    try:
        response = requests.get(f"https://avatar.roblox.com/v1/outfits/{outfitid}/details")
        response.raise_for_status()
        user_data = response.json()
        Name = user_data.get("name", "name not found")
        embed.add_field(name="Name", value=Name, inline=True)
    except requests.RequestException as e:
        embed.add_field(name="Error", value=f"Failed to fetch player info: {e}", inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="info", description="Info of the bot.")
async def info(interaction: discord.Interaction):
    embed = discord.Embed(title="Info", description="DiscBlox is a roblox intergrated discord bot.", color=0x6495ED)
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar)
    embed.set_thumbnail(url=bot.user.avatar)
    embed.add_field(name="Creation Date:", value="13/01/2024", inline=False)
    embed.add_field(name="Developer:", value="L.amb", inline=False)
    embed.set_footer(
        text="This command will be removed next update! Will be replaced with /info (Temporarily called /info-new)")
    await interaction.response.send_message(embed=embed)


bot.run('') #Put your token here!
