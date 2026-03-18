import discord
import random
import aiohttp
import os
import json
import re
from datetime import datetime
from discord.ext import commands

TOKEN = os.getenv("TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="", intents=intents)

# =========================
# 💾 MEMORY
# =========================
MEMORY_FILE = "memory.json"

if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w") as f:
        json.dump({}, f)

def load_memory():
    return json.load(open(MEMORY_FILE))

def save_memory(data):
    json.dump(data, open(MEMORY_FILE, "w"), indent=2)

def update_memory(uid, msg):
    data = load_memory()
    if str(uid) not in data:
        data[str(uid)] = []
    data[str(uid)].append(msg)
    data[str(uid)] = data[str(uid)][-10:]
    save_memory(data)

# =========================
# 🎬 GIF
# =========================
ACTIONS = ["kiss","hug","slap","punch","kick","cry","blush","laugh"]

async def get_gif(action):
    try:
        url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q=anime+{action}&limit=30"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                data = await r.json()
        gifs = [g["images"]["original"]["url"] for g in data["data"]]
        return random.choice(gifs)
    except:
        return None

# =========================
# 🌡️ WEATHER
# =========================
async def get_weather():
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get("https://wttr.in/Delhi?format=3") as r:
                return await r.text()
    except:
        return "Delhi ~30°C ☀️"

# =========================
# 💬 AI (SMART)
# =========================
async def ai_reply(msg):
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {
                            "role": "system",
                            "content":
                            "You are Sky, flirty but helpful. If user asks how to make something, give simple steps."
                        },
                        {"role": "user", "content": msg}
                    ]
                }
            ) as r:
                data = await r.json()

        return data["choices"][0]["message"]["content"][:120]
    except:
        return "idk 😭"

# =========================
# 🚀 MAIN
# =========================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    msg = message.content.strip()
    lower = msg.lower()

    # =====================
    # 🔥 PREFIX COMMANDS
    # =====================

    # .spam100 tiger
    if lower.startswith(".spam"):
        match = re.match(r"\.spam(\d+)\s+(.+)", lower)

        if match:
            count = min(int(match.group(1)), 50)
            text = match.group(2)

            for _ in range(count):
                await message.channel.send(text)
            return

    # .choose
    if lower.startswith(".choose"):
        options = msg.split()[1:]
        await message.channel.send(random.choice(options))
        return

    # .8ball
    if lower.startswith(".8ball"):
        await message.channel.send(random.choice([
            "yes 😏","no 💀","maybe 👀","definitely 😂","never 😭"
        ]))
        return

    # .flip
    if lower.startswith(".flip"):
        await message.channel.send(random.choice(["heads","tails"]))
        return

    # .roll
    if lower.startswith(".roll"):
        await message.channel.send(f"🎲 {random.randint(1,6)}")
        return

    # .roast
    if lower.startswith(".roast"):
        await message.channel.send(random.choice([
            "bro has wifi but no brain 💀",
            "you lag in real life 😂",
            "even google can’t fix you 😭"
        ]))
        return

    # =====================
    # SKY TRIGGER
    # =====================
    is_reply = False
    if message.reference:
        try:
            m = await message.channel.fetch_message(message.reference.message_id)
            if m.author == bot.user:
                is_reply = True
        except:
            pass

    trigger = (
        lower.startswith("sky") or
        bot.user in message.mentions or
        is_reply
    )

    if not trigger:
        return

    if lower.startswith("sky"):
        msg = msg[3:].strip()
        lower = msg.lower()

    # =====================
    # GIF
    # =====================
    for act in ACTIONS:
        if act in lower:
            gif = await get_gif(act)
            if gif:
                await message.channel.send(gif)
            return

    # =====================
    # WEATHER
    # =====================
    if "weather" in lower or "temp" in lower:
        await message.channel.send(await get_weather())
        return

    # =====================
    # MEMORY
    # =====================
    update_memory(message.author.id, msg)

    # =====================
    # AI
    # =====================
    reply = await ai_reply(msg)
    await message.channel.send(reply)

bot.run(TOKEN)
