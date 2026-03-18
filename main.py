import discord
import random
import aiohttp
import os
import json
import re
import asyncio
from discord.ext import commands, tasks

TOKEN = os.getenv("TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="", intents=intents)

# =========================
# 🔥 ROAST LIST (BIG)
# =========================
ROASTS = [
    "bro has wifi but no brain 💀",
    "you lag in real life 😂",
    "even google can't fix you 😭",
    "you proof evolution can go backward 💀",
    "you got 2 braincells fighting 😏",
    "npc behavior fr 😂",
    "you load slower than internet explorer 💀",
    "you exist just to lower average iq 😭",
    "your thoughts buffering rn 💀",
    "you type like autocorrect gave up 😂",
    "you built like a loading screen 😭",
    "you thought that was smart? 😏",
]

# =========================
# 😂 JOKES
# =========================
JOKES = [
    "why don’t programmers like nature? too many bugs 💀",
    "i told my code a joke… it didn’t compile 😭",
    "why did the dev go broke? used up all cache 😂",
    "why python devs so calm? no semicolons 😏",
]

# =========================
# 💬 AI (MORE HUMAN)
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
                            "You are Sky, a real human-like girl. Talk naturally, sometimes short, sometimes longer, be playful, slightly flirty, not robotic."
                        },
                        {"role": "user", "content": msg}
                    ],
                    "temperature": 1.2
                }
            ) as r:
                data = await r.json()

        return data["choices"][0]["message"]["content"][:120]

    except:
        return "hmm idk but you're interesting tho 😏"

# =========================
# 🔁 SPAM
# =========================
def parse_spam(msg):
    match = re.match(r"\.spam(\d+)\s+(.+)", msg)
    if match:
        count = min(int(match.group(1)), 50)
        text = match.group(2)
        return count, text
    return None, None

# =========================
# 🎬 GIF
# =========================
ACTIONS = ["kiss","hug","slap","punch","kick","cry","blush","laugh"]

async def get_gif(action):
    try:
        url = f"https://api.giphy.com/v1/gifs/search?api_key={os.getenv('GIPHY_API_KEY')}&q=anime+{action}&limit=30"
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                data = await r.json()

        gifs = [g["images"]["original"]["url"] for g in data["data"]]
        return random.choice(gifs)
    except:
        return None

# =========================
# ⏰ AUTO JOKE LOOP
# =========================
@tasks.loop(minutes=10)
async def auto_joke():
    for guild in bot.guilds:
        for channel in guild.text_channels:
            try:
                await channel.send(
                    random.choice(JOKES)
                )
                break
            except:
                continue

# =========================
# 🚀 MAIN
# =========================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    auto_joke.start()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    msg = message.content.strip()
    lower = msg.lower()

    # =====================
    # 🔥 PREFIX COMMANDS
    # =====================

    count, text = parse_spam(lower)
    if count:
        for _ in range(count):
            await message.channel.send(text)
        return

    if lower.startswith(".roast"):
        await message.channel.send(random.choice(ROASTS))
        return

    if lower.startswith(".joke"):
        await message.channel.send(random.choice(JOKES))
        return

    if lower.startswith(".flip"):
        await message.channel.send(random.choice(["heads","tails"]))
        return

    if lower.startswith(".roll"):
        await message.channel.send(f"🎲 {random.randint(1,6)}")
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
    # AI CHAT
    # =====================
    reply = await ai_reply(msg)
    await message.channel.send(reply)

bot.run(TOKEN)
