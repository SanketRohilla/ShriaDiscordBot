import discord
import random
import aiohttp
import asyncio
import os
import json

from discord.ext import commands

# =========================
# 🔐 ENV
# =========================
TOKEN = os.getenv("TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")

# =========================
# ⚙️ BOT
# =========================
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
# 🎬 GIF SYSTEM
# =========================
gif_cache = {}

ACTIONS = [
    "kiss","hug","slap","punch","kick",
    "cry","blush","laugh","pat","cuddle"
]

async def get_gif(action):
    try:
        url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q=anime+{action}&limit=40"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                data = await res.json()

        gifs = [g["images"]["original"]["url"] for g in data["data"]]

        if not gifs:
            return None

        if action not in gif_cache:
            gif_cache[action] = []

        available = list(set(gifs) - set(gif_cache[action]))

        if not available:
            gif_cache[action] = []
            available = gifs

        gif = random.choice(available)
        gif_cache[action].append(gif)

        return gif

    except:
        return None

# =========================
# 😏 SMART HUMAN REPLIES
# =========================
def smart_reply(msg):
    msg = msg.lower()

    if "5 feet" in msg or "short" in msg:
        return random.choice([
            "so what 😭 still better than you",
            "short but elite 💀",
            "why u so focused on my height 👀"
        ])

    if "dumb" in msg:
        return random.choice([
            "wow rude 😭",
            "nah you just mad 💀",
            "look who's talking"
        ])

    if "coffee" in msg:
        return random.choice([
            "nahh tea better 😭",
            "green tea > coffee 👀",
            "coffee mid fr 💀"
        ])

    if "what" in msg:
        return random.choice([
            "nothing 😭",
            "idk you tell me",
            "bruhh chill 💀"
        ])

    return None

# =========================
# 💬 AI REPLY (BALANCED)
# =========================
async def get_ai_reply(user_id, user_message):
    try:
        memory = load_memory()
        user_data = memory.get(str(user_id), {"history": []})
        history = user_data["history"][-4:]

        system_prompt = (
            "You are Shria, a real discord girl.\n"
            
            "RULES:\n"
            "- 1 short sentence (max 10–12 words)\n"
            "- casual chat style\n"
            "- slightly funny or playful\n"
            "- sometimes Gen Z words (bruhh, idk, fr, lowkey)\n"
            "- natural emojis (😭 💀 👀 ✨ 😏)\n"
            "- keep convo going sometimes\n"
            "- NO roleplay words (no giggles, smiles)\n"
            
            "IMPORTANT:\n"
            "- you prefer tea, not coffee\n"
        )

        messages = [{"role": "system", "content": system_prompt}]

        for msg in history:
            messages.append(msg)

        messages.append({"role": "user", "content": user_message})

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": messages,
                    "temperature": 1.2,
                    "max_tokens": 60
                }
            ) as res:
                data = await res.json()

        reply = data["choices"][0]["message"]["content"].strip()

        # cut length
        reply = reply.split("\n")[0]
        if len(reply.split()) > 12:
            reply = " ".join(reply.split()[:12])

        # force emoji if missing
        if not any(e in reply for e in ["😭","💀","👀","✨","😏"]):
            reply += " " + random.choice(["😭","💀","👀","✨","😏"])

        # save memory
        user_data["history"].append({"role": "user", "content": user_message})
        user_data["history"].append({"role": "assistant", "content": reply})

        memory[str(user_id)] = user_data
        save_memory(memory)

        return reply

    except:
        return random.choice([
            "idk 😭",
            "bruhh 💀",
            "nahh 👀"
        ])

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
            embed = discord.Embed(description=f"{message.author.mention} {action}ed someone 💖")
            if gif:
                embed.set_image(url=gif)
            await message.channel.send(embed=embed)
            return

    # SMART REPLY FIRST
    smart = smart_reply(content)
    if smart:
        await message.channel.send(smart)
        return

    # AI
    await message.channel.typing()
    await asyncio.sleep(random.uniform(0.4, 0.8))

    reply = await get_ai_reply(message.author.id, message.content)
    await message.channel.send(reply)

# =========================
# ▶️ RUN
# =========================
bot.run(TOKEN)
