import discord
import random
import aiohttp
import asyncio
import os
import json

from discord.ext import commands

TOKEN = os.getenv("TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="", intents=intents)

# =========================
# 💾 MEMORY
# =========================
MEMORY_FILE = "memory.json"

if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w") as f:
        json.dump({}, f)

def load_memory():
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

# =========================
# 🎬 GIF CACHE
# =========================
gif_cache = {}

ACTIONS = ["kiss","hug","slap","punch","kick","cry","blush","laugh"]

async def get_gif(action):
    try:
        url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q=anime+{action}&limit=50"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                data = await res.json()

        gifs = [g["images"]["original"]["url"] for g in data["data"]]

        return random.choice(gifs) if gifs else None
    except:
        return None

# =========================
# 😏 SMART COMEBACK SYSTEM
# =========================

def smart_reply(msg):
    msg = msg.lower()

    # HEIGHT / TEASING
    if "5 feet" in msg or "short" in msg:
        return random.choice([
            "so what 😭",
            "still cute tho 👀",
            "short but elite 💀",
            "height ain’t everything lol",
            "why u pressed 😭"
        ])

    # INSULT
    if "dumb" in msg or "stupid" in msg:
        return random.choice([
            "look who's talking 💀",
            "you started it 😭",
            "nah that’s you",
            "bruhh relax",
        ])

    # COFFEE
    if "coffee" in msg:
        return random.choice([
            "nah tea better 😭",
            "green tea tbh 👀",
            "coffee mid 💀",
            "not really"
        ])

    return None

# =========================
# 💬 AI
# =========================
async def get_ai_reply(user_message):
    try:
        system_prompt = (
            "You are Shria, a real discord girl.\n"
            "- Talk casually like a normal person\n"
            "- Mix short and medium replies\n"
            "- Sometimes tease\n"
            "- Keep it natural, not AI\n"
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "temperature": 1.2
                }
            ) as res:
                data = await res.json()

        reply = data["choices"][0]["message"]["content"]
        return reply.split("\n")[0][:80]

    except:
        return random.choice(["idk 😭", "bruhh 💀", "nahh"])

# =========================
# 🚀 READY
# =========================
@bot.event
async def on_ready():
    print(f"💖 Logged in as {bot.user}")

# =========================
# 💬 MAIN
# =========================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()

    is_called = (
        "shria" in content or
        bot.user in message.mentions
    )

    if not is_called:
        return

    # GIF
    for action in ACTIONS:
        if action in content:
            gif = await get_gif(action)
            embed = discord.Embed(description=f"{message.author.mention} {action}ed someone 😭")
            if gif:
                embed.set_image(url=gif)
            await message.channel.send(embed=embed)
            return

    # 🔥 SMART REPLY FIRST
    reply = smart_reply(content)

    if reply:
        await message.channel.send(reply)
        return

    # AI fallback
    await message.channel.typing()
    await asyncio.sleep(random.uniform(0.3, 0.7))

    reply = await get_ai_reply(message.content)
    await message.channel.send(reply)

bot.run(TOKEN)
