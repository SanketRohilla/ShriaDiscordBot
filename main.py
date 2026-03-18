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
# 🔥 ROASTS
# =========================
ROASTS = [
    "bro your brain on airplane mode 💀",
    "you type like lag is permanent 😂",
    "even google gave up on you 😭",
    "you built like a loading screen 💀",
    "npc behavior fr 😂",
    "your iq buffering rn 💀",
    "you got 2 braincells fighting 😏",
    "bro thought he did something 💀",
    "you not dumb, just special edition 😂",
    "you are the reason tutorials exist 😭"
]

# =========================
# 🍳 RECIPE (AI FOR FOOD ONLY)
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
                        {
                            "role": "system",
                            "content":
                            "Give short simple step-by-step recipe. max 5 steps."
                        },
                        {"role": "user", "content": f"how to make {food}"}
                    ]
                }
            ) as r:
                data = await r.json()

        return data["choices"][0]["message"]["content"][:200]
    except:
        return "idk just youtube it 😭"

# =========================
# 🎬 GIF
# =========================
ACTIONS = ["kiss","hug","slap","punch","kick","cry","blush","laugh"]

async def get_gif(action):
    try:
        url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q=anime+{action}&limit=30"
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                data = await r.json()

        gifs = [g["images"]["original"]["url"] for g in data["data"]]
        return random.choice(gifs)
    except:
        return None

# =========================
# 💬 AI NORMAL CHAT
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
                            "You are Sky, real human-like girl, short, fun, flirty, not long replies."
                        },
                        {"role": "user", "content": msg}
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
    # 🔥 ROAST SYSTEM
    # =====================
    if "roast" in lower:

        # roast everyone
        if "everyone" in lower:
            await message.channel.send(
                f"@everyone {random.choice(ROASTS)}",
                allowed_mentions=discord.AllowedMentions(everyone=True)
            )
            return

        # roast mentioned user
        if message.mentions:
            target = message.mentions[0]
            await message.channel.send(f"{target.mention} {random.choice(ROASTS)}")
            return

        # roast self
        await message.channel.send(f"{message.author.mention} {random.choice(ROASTS)}")
        return

    # =====================
    # 🍳 RECIPE SYSTEM
    # =====================
    if "how to make" in lower or "recipe" in lower:
        food = lower.replace("how to make", "").replace("recipe", "").strip()
        res = await recipe_ai(food)
        await message.channel.send(res)
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
    # 💬 NORMAL CHAT
    # =====================
    reply = await ai_reply(msg)
    await message.channel.send(reply)

bot.run(TOKEN)
