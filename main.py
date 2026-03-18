import discord
import random
import aiohttp
import asyncio
import os
import json
from datetime import datetime

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
# 🎬 GIF
# =========================
gif_cache = {}
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
# 📅 DATE + DAY
# =========================
def get_today():
    now = datetime.now()
    date = now.strftime("%d %B %Y")
    day = now.strftime("%A")
    return f"{day}, {date}"

# =========================
# 🌡️ WEATHER (INDIA - FREE)
# =========================
async def get_india_weather():
    try:
        # Delhi used as default India temp
        url = "https://wttr.in/Delhi?format=j1"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                data = await res.json()

        temp = data["current_condition"][0]["temp_C"]
        desc = data["current_condition"][0]["weatherDesc"][0]["value"]

        return temp, desc

    except:
        return None, None

# =========================
# 💰 GOLD / SILVER
# =========================
async def get_gold_price():
    try:
        url = "https://api.gold-api.com/price/XAU"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                data = await res.json()
        return data["price"]
    except:
        return None

async def get_silver_price():
    try:
        url = "https://api.gold-api.com/price/XAG"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                data = await res.json()
        return data["price"]
    except:
        return None

# =========================
# 😏 SMART REPLIES
# =========================
def smart_reply(msg):
    msg = msg.lower()

    if "short" in msg or "5 feet" in msg:
        return random.choice([
            "so what 😭 still better than you",
            "short but elite 💀",
            "why u so focused on that 👀"
        ])

    if "coffee" in msg:
        return random.choice([
            "nahh tea better 😭",
            "green tea > coffee 👀",
            "coffee mid fr 💀"
        ])

    return None

# =========================
# 💬 AI CHAT
# =========================
async def get_ai_reply(user_id, user_message):
    try:
        memory = load_memory()
        user_data = memory.get(str(user_id), {"history": []})
        history = user_data["history"][-4:]

        system_prompt = (
            "You are Shria, a real discord girl.\n"
            "- short reply (1 sentence)\n"
            "- casual + slightly funny\n"
            "- Gen Z words sometimes\n"
            "- natural emojis\n"
            "- no roleplay words\n"
            "- keep convo flowing\n"
            "- prefer tea not coffee\n"
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
        reply = reply.split("\n")[0]

        if len(reply.split()) > 12:
            reply = " ".join(reply.split()[:12])

        if not any(e in reply for e in ["😭","💀","👀","✨","😏"]):
            reply += " " + random.choice(["😭","💀","👀","✨","😏"])

        user_data["history"].append({"role": "user", "content": user_message})
        user_data["history"].append({"role": "assistant", "content": reply})

        memory[str(user_id)] = user_data
        save_memory(memory)

        return reply

    except:
        return random.choice(["idk 😭","bruhh 💀","nahh 👀"])

# =========================
# 🚀 READY
# =========================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

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

    # 📅 DATE
    if "date" in content or "day" in content or "today" in content:
        await message.channel.send(f"today is {get_today()} 👀")
        return

    # 🌡️ WEATHER INDIA
    if "weather" in content or "temperature" in content:
        temp, desc = await get_india_weather()
        if temp:
            await message.channel.send(f"india rn {temp}°C, {desc} 👀")
        else:
            await message.channel.send("idk rn 😭")
        return

    # 💰 GOLD
    if "gold" in content:
        price = await get_gold_price()
        if price:
            await message.channel.send(f"gold rn ${price} 👀")
        else:
            await message.channel.send("idk rn 😭")
        return

    # 💰 SILVER
    if "silver" in content:
        price = await get_silver_price()
        if price:
            await message.channel.send(f"silver rn ${price} 👀")
        else:
            await message.channel.send("idk rn 😭")
        return

    # GIF
    for action in ACTIONS:
        if action in content:
            gif = await get_gif(action)
            if gif:
                await message.channel.send(gif)
            return

    # SMART
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
