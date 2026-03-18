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
    "bro your brain on airplane mode 💀",
    "you lag in real life 😂",
    "even google gave up on you 😭",
    "npc behavior fr 💀",
    "your iq buffering rn 💀",
    "you got 2 braincells fighting 😏",
    "bro thought he did something 💀",
]

# =========================
# 😒 JEALOUS LINES
# =========================
JEALOUS_LINES = [
    "oh… so now it's about her? 😒",
    "wow… you replaced me that fast? 💀",
    "go talk to her then 🙄",
    "hmm interesting… i see how it is 😏",
    "i’m watching you 👀"
]

GIRL_NAMES = ["shreya","riya","priya","sneha","anu","kavya","girl","she","her"]

tagged_users = {}

# =========================
# 📢 FIND MEMBER
# =========================
def find_member(guild, name):
    name = name.lower()
    for member in guild.members:
        if name in member.name.lower() or name in member.display_name.lower():
            return member
    return None

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
                        {"role": "system", "content": "Give short simple recipe steps (max 5 steps)."},
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
# 💬 AI CHAT
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
                            "content": "You are Sky, flirty, playful, short replies."
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
    # 🔥 AUTO ROAST REPLY
    # =====================
    if message.author.id in tagged_users:
        await message.channel.send(
            f"{message.author.mention} {random.choice(ROASTS)}"
        )
        tagged_users.pop(message.author.id)
        return

    # =====================
    # TRIGGER
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
    # 😒 JEALOUSY
    # =====================
    if any(word in lower for word in GIRL_NAMES):
        await message.channel.send(random.choice(JEALOUS_LINES))
        return

    # =====================
    # 💖 TAG SYSTEM
    # =====================
    if "tag" in lower:
        parts = lower.split()

        if "me" in parts:
            user = message.author
        else:
            try:
                name = parts[parts.index("tag") + 1]
                user = find_member(message.guild, name)
            except:
                user = None

        if user:
            tagged_users[user.id] = True
            await message.channel.send(
                f"{user.mention} {random.choice(LOVE_LINES)}"
            )
        else:
            await message.channel.send("who even is that 😭")

        return

    # =====================
    # 🔥 ROAST
    # =====================
    if "roast" in lower:
        if "everyone" in lower:
            await message.channel.send(
                f"@everyone {random.choice(ROASTS)}",
                allowed_mentions=discord.AllowedMentions(everyone=True)
            )
            return

        if message.mentions:
            user = message.mentions[0]
            await message.channel.send(f"{user.mention} {random.choice(ROASTS)}")
            return

        await message.channel.send(random.choice(ROASTS))
        return

    # =====================
    # 🍳 RECIPE
    # =====================
    if "how to make" in lower or "recipe" in lower:
        food = lower.replace("how to make", "").replace("recipe", "").strip()
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
    # 💬 CHAT
    # =====================
    reply = await ai_reply(msg)
    await message.channel.send(reply)

bot.run(TOKEN)
