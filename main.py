import discord
import random
import aiohttp
import os
import json
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
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def update_memory(user_id, msg):
    data = load_memory()

    if str(user_id) not in data:
        data[str(user_id)] = {"history": [], "style": "normal"}

    data[str(user_id)]["history"].append(msg)
    data[str(user_id)]["history"] = data[str(user_id)]["history"][-15:]

    if len(msg.split()) <= 4:
        data[str(user_id)]["style"] = "short"
    else:
        data[str(user_id)]["style"] = "normal"

    save_memory(data)

def get_memory(user_id):
    data = load_memory()
    return data.get(str(user_id), {"history": [], "style": "normal"})

# =========================
# 🎬 GIF SYSTEM
# =========================
ACTIONS = ["kiss","hug","slap","punch","kick","cry","blush","laugh"]

async def get_gif(action):
    try:
        url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q=anime+{action}&limit=40"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                data = await res.json()

        gifs = [g["images"]["original"]["url"] for g in data["data"]]

        return random.choice(gifs) if gifs else None
    except:
        return None

# =========================
# 🔁 SAY
# =========================
def parse_say(msg):
    words = msg.split()
    if "say" in words or "type" in words:
        try:
            i = words.index("say") if "say" in words else words.index("type")
            text = words[i+1]
            count = int(words[i+2])
            return text, min(count, 50)
        except:
            return None, None
    return None, None

# =========================
# 🌡️ WEATHER
# =========================
async def get_weather():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://wttr.in/Delhi?format=3") as res:
                return await res.text()
    except:
        return "Delhi ~30°C rn ☀️"

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
# 💋 EMOJI
# =========================
def emoji():
    return random.choice(["😏","👀","😂","💀","✨","😉"])

# =========================
# 💬 AI
# =========================
async def ai_reply(user_id, msg):
    try:
        mem = get_memory(user_id)
        history = "\n".join(mem["history"])
        style = mem["style"]

        style_instruction = (
            "Reply short and casual."
            if style == "short"
            else "Reply naturally."
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
                        {
                            "role": "system",
                            "content":
                            f"You are Sky, a flirty, playful girl. {style_instruction}"
                        },
                        {
                            "role": "user",
                            "content": f"Past chats:\n{history}\n\nNow:\n{msg}"
                        }
                    ]
                }
            ) as res:
                data = await res.json()

        reply = data["choices"][0]["message"]["content"].split("\n")[0][:120]
        return f"{reply} {emoji()}"

    except:
        return f"hmm idk but ur vibe nice {emoji()}"

# =========================
# 🚀 MAIN
# =========================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.strip()
    lower = content.lower()

    # reply detection
    is_reply = False
    if message.reference:
        try:
            msg = await message.channel.fetch_message(message.reference.message_id)
            if msg.author == bot.user:
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

    # remove "sky"
    if lower.startswith("sky"):
        content = content[3:].strip()
        lower = content.lower()

    # =====================
    # 🎬 GIF COMMAND
    # =====================
    for action in ACTIONS:
        if action in lower:
            gif = await get_gif(action)
            if gif:
                await message.channel.send(gif)
            else:
                await message.channel.send("no gif found 😭")
            return

    # =====================
    # 📢 TAG SYSTEM
    # =====================
    if "tag" in lower:

        if "everyone" in lower:
            await message.channel.send(
                "@everyone wake up 😏",
                allowed_mentions=discord.AllowedMentions(everyone=True)
            )
            return

        if "me" in lower:
            await message.channel.send(f"{message.author.mention} there u go 😏")
            return

        parts = lower.split()

        try:
            name = parts[parts.index("tag") + 1]
            member = find_member(message.guild, name)

            if member:
                await message.channel.send(f"{member.mention} come here 👀")
            else:
                await message.channel.send("who even is that 😭")

        except:
            await message.channel.send("tag who exactly? 😭")

        return

    # 🔁 SAY
    text, count = parse_say(lower)
    if text:
        await message.channel.send("ok chill 😭")
        await message.channel.send(" ".join([text]*count))
        return

    # 🌡️ WEATHER
    if "temp" in lower or "weather" in lower:
        await message.channel.send(await get_weather())
        return

    # 💾 MEMORY
    update_memory(message.author.id, content)

    # 💬 AI
    reply = await ai_reply(message.author.id, content)
    await message.channel.send(reply)

bot.run(TOKEN)
