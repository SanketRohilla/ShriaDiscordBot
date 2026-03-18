import discord
import random
import aiohttp
import os
import re
from discord.ext import commands

TOKEN = os.getenv("TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="", intents=intents)

# =========================
# 💖 LOVE LINES
# =========================
LOVE_LINES = [
    "you looking kinda cute today 😏",
    "why you always this fine huh 👀",
    "stop being this attractive it's illegal 😭",
    "lowkey got a crush on you ngl 💕",
    "you just made the chat better by existing ✨",
    "i see you… and i like what i see 😏",
]

# =========================
# 🔥 ROASTS
# =========================
ROASTS = [
    "bro came back just to embarrass himself 💀",
    "you thought that reply was smart? 😭",
    "your brain on airplane mode again 😂",
    "npc response fr 💀",
    "you really said that out loud huh 😏",
]

# store tagged users
tagged_users = {}

# =========================
# 🍳 RECIPE
# =========================
async def recipe_ai(food):
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
                        {"role": "system", "content": "give short recipe steps"},
                        {"role": "user", "content": f"how to make {food}"}
                    ]
                }
            ) as r:
                data = await r.json()

        return data["choices"][0]["message"]["content"][:200]
    except:
        return "idk 😭"

# =========================
# 🎬 GIF
# =========================
ACTIONS = ["kiss","hug","slap","punch","kick"]

async def get_gif(action):
    try:
        url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q=anime+{action}&limit=20"
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                data = await r.json()

        gifs = [g["images"]["original"]["url"] for g in data["data"]]
        return random.choice(gifs)
    except:
        return None

# =========================
# 💬 AI
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
                        {"role": "system","content":"short human-like flirty replies"},
                        {"role": "user","content": msg}
                    ]
                }
            ) as r:
                data = await r.json()

        return data["choices"][0]["message"]["content"][:100]
    except:
        return "idk 😏"

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
    # 🔥 REPLY ROAST SYSTEM
    # =====================
    if message.author.id in tagged_users:
        await message.channel.send(
            f"{message.author.mention} {random.choice(ROASTS)}"
        )
        tagged_users.pop(message.author.id)
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
    # 💖 LOVE TAG
    # =====================
    if message.mentions:
        user = message.mentions[0]

        tagged_users[user.id] = True

        await message.channel.send(
            f"{user.mention} {random.choice(LOVE_LINES)}"
        )
        return

    # =====================
    # 🍳 RECIPE
    # =====================
    if "how to make" in lower:
        food = lower.replace("how to make", "").strip()
        await message.channel.send(await recipe_ai(food))
        return

    # =====================
    # 🎬 GIF
    # =====================
    for act in ACTIONS:
        if act in lower:
            gif = await get_gif(act)
            if gif:
                await message.channel.send(gif)
            return

    # =====================
    # 💬 AI CHAT
    # =====================
    reply = await ai_reply(msg)
    await message.channel.send(reply)

bot.run(TOKEN)
