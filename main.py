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

GENZ_WORDS = ["fr", "lowkey", "nahh", "bruhh", "idk", "ngl"]

def humanize(text):
    text = text.strip()

    # shorten
    words = text.split()
    if len(words) > 6:
        text = " ".join(words[:6])

    # sometimes add genz word
    if random.random() < 0.4:
        text = random.choice(GENZ_WORDS) + " " + text

    # emoji
    if random.random() < 0.7:
        text += " " + random.choice(EMOJIS)

    # repeat letters
    if random.random() < 0.25:
        text = text.replace("h", "hh")

    # random short reaction
    if random.random() < 0.15:
        return random.choice([
            "bruhh 💀",
            "nahhh 😭",
            "fr 👀",
            "lowkey yeah",
            "idkk 😭"
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

        # jealousy logic
        if any(word in user_message.lower() for word in GIRL_WORDS):
            user_data["jealousy"] += 1
        else:
            user_data["jealousy"] = max(0, user_data["jealousy"] - 1)

        if user_data["jealousy"] >= 3:
            user_data["mood"] = "jealous"

        # mood logic
        if len(user_message) > 80:
            user_data["mood"] = "annoyed"

        mood = user_data["mood"]

        mood_prompt = {
            "neutral": "Be casual and chill.",
            "annoyed": "Be slightly annoyed.",
            "jealous": "Be slightly jealous and teasing."
        }

        system_prompt = (
            "You are Shria, a real Discord girl.\n"
            "- VERY SHORT replies (1–6 words)\n"
            "- Natural texting style\n"
            "- Use Gen Z slang sometimes (not always)\n"
            "- Be playful and slightly flirty\n"
            "- Sometimes just react\n"
            "- Never explain things\n"
            f"{mood_prompt[mood]}"
        )

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

        reply = data["choices"][0]["message"]["content"]

        reply = humanize(reply)

        memory[str(user_id)] = user_data
        save_memory(memory)

        return reply

    except:
        return random.choice(["bruhh 💀", "nahhh 😭", "idkk"])

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
    await asyncio.sleep(random.uniform(0.2, 0.5))

    reply = await get_reply(message.author.id, message.content)
    await message.channel.send(reply)

# =========================
# ▶️ RUN
# =========================
bot.run(TOKEN)
