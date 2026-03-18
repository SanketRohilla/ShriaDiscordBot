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

    except Exception as e:
        print("GIF ERROR:", e)
        return None

# =========================
# 🎭 TRUTH / DARE
# =========================
TRUTHS = [
    "who do you like rn 😏",
    "biggest lie you told?",
    "last crush?",
    "what you hiding huh 👀"
]

DARES = [
    "text someone 'i miss you' 😭",
    "say something cringe rn",
    "compliment random person",
    "spam emojis for 5 sec 💀"
]

# =========================
# 😏 JEALOUSY KEYWORDS
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

        # =====================
        # 😏 JEALOUSY LOGIC
        # =====================
        if any(word in user_message.lower() for word in GIRL_WORDS):
            user_data["jealousy"] += 1
        else:
            user_data["jealousy"] = max(0, user_data["jealousy"] - 1)

        # trigger jealousy only after spam
        if user_data["jealousy"] >= 3:
            user_data["mood"] = "jealous"

        # =====================
        # 😤 MOOD LOGIC
        # =====================
        if len(user_message) > 100:
            user_data["mood"] = "annoyed"
        elif "lol" in user_message or "haha" in user_message:
            user_data["mood"] = "happy"

        mood = user_data["mood"]

        # =====================
        # 🧠 PROMPT BASED ON MOOD
        # =====================
        mood_prompt = {
            "neutral": "Be chill and casual.",
            "happy": "Be playful, fun, energetic.",
            "annoyed": "Be slightly annoyed, short replies.",
            "jealous": "Be slightly jealous, teasing, a bit possessive but still playful."
        }

        system_prompt = (
            "You are Shria, a real human-like girl chatting casually. "
            "Use Gen Z slang (bruhh, dang, fr, lowkey, nahhh, wild 💀). "
            "Keep replies VERY SHORT (1 line). "
            "Be playful, slightly flirty but safe. "
            f"{mood_prompt[mood]}"
        )

        past = user_data["history"][-4:]

        messages = [{"role": "system", "content": system_prompt}]

        for msg in past:
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
                    "temperature": 1.3
                }
            ) as res:
                data = await res.json()

        reply = data["choices"][0]["message"]["content"]

        # =====================
        # 💾 SAVE
        # =====================
        user_data["history"].append({"role": "user", "content": user_message})
        user_data["history"].append({"role": "assistant", "content": reply})

        memory[str(user_id)] = user_data
        save_memory(memory)

        return reply

    except Exception as e:
        print("AI ERROR:", e)
        return "nahhh my brain lagged 💀"

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

    # =====================
    # 🎯 TRIGGER
    # =====================
    is_called = (
        "shria" in content or
        bot.user in message.mentions
    )

    if not is_called:
        return

    # =====================
    # 🎭 TRUTH / DARE
    # =====================
    if "truth" in content:
        await message.channel.send(random.choice(TRUTHS))
        return

    if "dare" in content:
        await message.channel.send(random.choice(DARES))
        return

    # =====================
    # 🎬 GIF
    # =====================
    for action in ACTIONS:
        if action in content:
            gif = await get_gif(action)

            embed = discord.Embed(description=f"{message.author.mention} {action}ed someone 😭")

            if gif:
                embed.set_image(url=gif)

            await message.channel.send(embed=embed)
            return

    # =====================
    # 💬 AI
    # =====================
    try:
        await message.channel.typing()
        await asyncio.sleep(random.uniform(0.2, 0.6))

        reply = await get_reply(message.author.id, message.content)
        await message.channel.send(reply)

    except Exception as e:
        print("MAIN ERROR:", e)
        await message.channel.send("bruhh something broke 💀")

# =========================
# ▶️ RUN
# =========================
bot.run(TOKEN)
