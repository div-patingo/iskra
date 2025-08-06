from keep_alive import keep_alive
import discord
import requests
import asyncio
import json
from dotenv import load_dotenv
import os
from flask import Flask
from threading import Thread

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TORN_API_KEY = os.getenv("TORN_API_KEY")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Bot is up!"

@app.route("/run")
def trigger_report():
    asyncio.run_coroutine_threadsafe(send_report(), client.loop)
    return "📨 Report triggered!"

def start_flask():
    app.run(host="0.0.0.0", port=8080)

def fetch_faction_members():
    url = f"https://api.torn.com/faction/?selections=basic&key={TORN_API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch faction members:", response.status_code)
        return {}
    data = response.json()
    return data.get("members", {})

async def send_report():
    await client.wait_until_ready()
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

# Start Flask server in a separate thread
flask_thread = Thread(target=start_flask)
flask_thread.start()

# Start Discord bot
keep_alive()
client.run(DISCORD_TOKEN)
