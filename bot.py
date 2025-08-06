import discord
import requests
import asyncio
import json
from dotenv import load_dotenv
import os

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TORN_API_KEY = os.getenv("TORN_API_KEY")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

def fetch_faction_members():
    url = f"https://api.torn.com/faction/?selections=basic&key={TORN_API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch faction members:", response.status_code)
        return {}
    data = response.json()
    return data.get("members", {})

async def send_report():
    channel = client.get_channel(CHANNEL_ID)
    report_lines = ["**📋 Torn Faction Members Status Report**"]

    faction_members = fetch_faction_members()

    if not faction_members:
        report_lines.append("❌ Unable to fetch members or access denied.")
    else:
        for user_id, member in faction_members.items():
            name = member.get("name", "Unknown")
            status = member.get("status", {}).get("description", "Unknown").capitalize()
            report_lines.append(f"{name} [{user_id}] - {status}")

    report = "\n".join(report_lines)
    await channel.send(report)

@client.event
async def on_ready():
    print(f'✅ Bot is live as {client.user}')
    await send_report()
    await client.close()

client.run(DISCORD_TOKEN)
