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
# 🎬 GIF CACHE
# =========================
gif_cache = {}

ACTIONS = [
    "kiss","hug","slap","punch","kick",
    "cry","blush","laugh",
    "pat","cuddle","bite","lick",
    "highfive","wave","dance","angry",
    "sleep","bored","smug","stare"
]

async def get_gif(action):
    try:
        url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q=anime+{action}&limit=50"

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
# 😏 STYLE ENGINE
# =========================
EMOJIS = ["😭", "💀", "👀", "✨", "😏", "🙂", "😒"]

def humanize(text):
    text = text.strip()

    # cut long
    words = text.split()
    if len(words) > 10:
        text = " ".join(words[:10])

    # emoji always (fix your issue)
    text += " " + random.choice(EMOJIS)

    # sometimes very short
    if random.random() < 0.25:
        return random.choice([
            "bruhh 💀",
            "idk 😭",
            "nahh 👀",
            "huh?",
            "what 😭"
        ])

    # sometimes medium messy
    if random.random() < 0.4:
        return random.choice([
            "idk tbh 😭",
            "lowkey weird 👀",
            "why u asking that 😏",
            "nahhh not really 💀",
            "maybe… idk ✨"
        ])

    return text

# =========================
# 😏 JEALOUSY
# =========================
GIRL_WORDS = ["girl", "her", "she", "gf", "crush", "babe"]

# =========================
# 💬 AI
# =========================
async def get_reply(user_id, user_message):
    try:
        memory = load_memory()

        user_data = memory.get(str(user_id), {
            "history": [],
            "mood": "neutral",
            "jealousy": 0
        })

        # jealousy
        if any(word in user_message.lower() for word in GIRL_WORDS):
            user_data["jealousy"] += 1
        else:
            user_data["jealousy"] = max(0, user_data["jealousy"] - 1)

        if user_data["jealousy"] >= 3:
            user_data["mood"] = "jealous"

        mood = user_data["mood"]

        system_prompt = (
            "You are Shria, a real discord girl.\n"
            "- mix short and medium replies\n"
            "- sometimes 1 word, sometimes 1 sentence\n"
            "- don't always answer directly\n"
            "- sometimes react or ask back\n"
            "- no AI tone\n"
            "- natural messy texting style\n"
            
            "IMPORTANT:\n"
            "- you hate coffee\n"
            "- you prefer tea or green tea\n"
        )

        if mood == "jealous":
            system_prompt += "\n- act slightly jealous and teasing"

        messages = [{"role": "system", "content": system_prompt}]
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
                    "temperature": 1.4
                }
            ) as res:
                data = await res.json()

        reply = data["choices"][0]["message"]["content"].strip().lower()

        # 🔥 HARD COFFEE FIX
        if "coffee" in reply:
            reply = random.choice([
                "nahh i dont like it",
                "tea better 😭",
                "green tea tbh 👀",
                "not really"
            ])

        reply = humanize(reply)

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
            embed = discord.Embed(description=f"{message.author.mention} {action}ed someone 😭")
            if gif:
                embed.set_image(url=gif)
            await message.channel.send(embed=embed)
            return

    # AI
    await message.channel.typing()
    await asyncio.sleep(random.uniform(0.3, 0.7))

    reply = await get_reply(message.author.id, message.content)
    await message.channel.send(reply)

# =========================
# ▶️ RUN
# =========================
bot.run(TOKEN)
