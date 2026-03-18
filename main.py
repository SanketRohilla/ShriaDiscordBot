import discord
import random
import aiohttp
import os
import re
from discord.ext import commands, tasks

TOKEN = os.getenv("TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="", intents=intents)

# =========================
# 💖 EMOJIS
# =========================
LOVE_EMOJIS = ["❤️","😍","😘","💕","💓","💞","💖","💗","💘"]
DANGER_EMOJIS = ["🔫","🔪","💣","⚔️","🗡️"]

def is_only_emoji(msg):
    return all(char in ''.join(LOVE_EMOJIS + DANGER_EMOJIS) for char in msg)

# =========================
# 💖 LOVE LINES
# =========================
LOVE_LINES = [
    "you looking kinda cute today 😏💕",
    "why you always this fine huh 👀💖",
    "lowkey got a crush on you ngl 😏💘",
    "you just made the chat better ✨💕",
]

# =========================
# 🔥 ROASTS
# =========================
ROASTS = [
    "bro your brain on airplane mode 💀",
    "npc behavior fr 💀😂",
    "you lag in real life 😭",
    "your iq buffering rn 💀",
]

# =========================
# 😒 JEALOUS
# =========================
JEALOUS_LINES = [
    "oh… so now it's about her? 😒",
    "go talk to her then 🙄",
    "wow… replaced me that fast? 💀",
]

GIRL_WORDS = ["she","her","girl","other girl"]

tagged_users = {}

# =========================
# 📢 FIND MEMBER
# =========================
def find_member(guild, name):
    name = name.lower()
    for m in guild.members:
        if name in m.name.lower() or name in m.display_name.lower():
            return m
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
                        {"role":"system","content":"give simple short recipe steps"},
                        {"role":"user","content": f"how to make {food}"}
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
                        {
                            "role":"system",
                            "content":"You are Sky, flirty and human-like. Always add 1 emoji in reply."
                        },
                        {"role":"user","content": msg}
                    ]
                }
            ) as r:
                data = await r.json()

        return data["choices"][0]["message"]["content"][:120]
    except:
        return "hmm idk 😏"

# =========================
# 💘 COUPLE SYSTEM (FIXED)
# =========================
@tasks.loop(hours=6)
async def couple_loop():
    await bot.wait_until_ready()

    for guild in bot.guilds:
        members = [m for m in guild.members if not m.bot]

        if len(members) < 2:
            continue

        m1, m2 = random.sample(members, 2)

        # find first usable channel
        channel = None
        for ch in guild.text_channels:
            if ch.permissions_for(guild.me).send_messages:
                channel = ch
                break

        if channel:
            await channel.send(
                f"💘 Sky ships {m1.mention} & {m2.mention} now 😏"
            )

# =========================
# 🚀 EVENTS
# =========================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    if not couple_loop.is_running():
        couple_loop.start()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    msg = message.content.strip()
    lower = msg.lower()

    # =====================
    # 💖 EMOJI SYSTEM (FIXED)
    # =====================
    if msg:
        if any(e in msg for e in DANGER_EMOJIS):
            await message.channel.send("why u gonna kill me like that 😭")
            return

        # only emoji message
        if re.fullmatch(r"[^\w\s]+", msg):
            await message.channel.send(random.choice(LOVE_EMOJIS))
            return

    # =====================
    # 🔥 REVENGE ROAST
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

    # jealousy
    if any(w in lower for w in GIRL_WORDS):
        await message.channel.send(random.choice(JEALOUS_LINES))
        return

    # tag
    if "tag" in lower:
        parts = lower.split()

        if "me" in parts:
            user = message.author
        else:
            try:
                name = parts[parts.index("tag")+1]
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

    # roast
    if "roast" in lower:
        if "everyone" in lower:
            await message.channel.send(
                f"@everyone {random.choice(ROASTS)}",
                allowed_mentions=discord.AllowedMentions(everyone=True)
            )
            return

        if message.mentions:
            u = message.mentions[0]
            await message.channel.send(f"{u.mention} {random.choice(ROASTS)}")
            return

        await message.channel.send(random.choice(ROASTS))
        return

    # recipe
    if "how to make" in lower:
        food = lower.replace("how to make","").strip()
        await message.channel.send(await recipe_ai(food))
        return

    # gif
    for act in ACTIONS:
        if act in lower:
            gif = await get_gif(act)
            if gif:
                await message.channel.send(gif)
            return

    # AI chat
    await message.channel.send(await ai_reply(msg))

bot.run(TOKEN)
