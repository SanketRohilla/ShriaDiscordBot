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
# 🎬 GIF
# =========================
ACTIONS = ["kiss","hug","slap","punch","kick","cry","blush","laugh"]

async def get_gif(action):
    try:
        url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q=anime+{action}&limit=30"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                data = await res.json()
        gifs = [g["images"]["original"]["url"] for g in data["data"]]
        return random.choice(gifs) if gifs else None
    except:
        return None

# =========================
# 📅 DATE
# =========================
def get_today():
    now = datetime.now()
    return f"{now.strftime('%A')}, {now.strftime('%d %B %Y')}"

# =========================
# 🌡️ WEATHER
# =========================
async def get_india_weather():
    try:
        url = "https://goweather.herokuapp.com/weather/Delhi"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                data = await res.json()
        return data.get("temperature"), data.get("description")
    except:
        return None, None

# =========================
# 💰 GOLD / SILVER
# =========================
async def get_gold_price():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.gold-api.com/price/XAU") as res:
                data = await res.json()
        return data["price"]
    except:
        return None

async def get_silver_price():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.gold-api.com/price/XAG") as res:
                data = await res.json()
        return data["price"]
    except:
        return None

async def usd_to_inr(usd):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://open.er-api.com/v6/latest/USD") as res:
                data = await res.json()
        return round(usd * data["rates"]["INR"], 2)
    except:
        return None

# =========================
# 📈 STOCKS
# =========================
STOCKS = {
    "reliance": "RELIANCE.NS",
    "tcs": "TCS.NS",
    "tata": "TCS.NS",
    "infosys": "INFY.NS",
    "infy": "INFY.NS",
    "hdfc": "HDFCBANK.NS"
}

async def get_stock_price(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                data = await res.json()

        result = data.get("quoteResponse", {}).get("result", [])
        if not result:
            return None, None

        return result[0]["shortName"], result[0]["regularMarketPrice"]
    except:
        return None, None

# =========================
# 🍳 RECIPE
# =========================
def is_serious_question(msg):
    return any(k in msg for k in ["how to","recipe","make","cook","steps"])

def get_simple_recipe(msg):
    if "cake" in msg:
        return "cake:\n1. mix flour, sugar, eggs\n2. add milk + butter\n3. bake 180°C 30min 🍰"
    if "tea" in msg:
        return "tea:\n1. boil water\n2. add tea + milk\n3. sugar ☕"
    if "bread" in msg:
        return "bread:\n1. flour + yeast\n2. knead\n3. bake 🍞"
    if "coffee" in msg:
        return "coffee:\n1. boil water\n2. add coffee\n3. milk ☕"
    return None

# =========================
# 🔁 SAY COMMAND
# =========================
def parse_say_command(msg):
    try:
        parts = msg.split()
        if "say" not in parts:
            return None, None

        i = parts.index("say")
        word = parts[i + 1]
        count = int(parts[i + 2])

        if count > 50:
            count = 50

        return word, count
    except:
        return None, None

# =========================
# 💬 AI
# =========================
async def get_ai_reply(user_message):
    try:
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
                        {"role": "system", "content": "short funny genz replies"},
                        {"role": "user", "content": user_message}
                    ]
                }
            ) as res:
                data = await res.json()

        reply = data["choices"][0]["message"]["content"].split("\n")[0][:80]

        if not any(e in reply for e in ["😭","💀","👀"]):
            reply += " 😭"

        return reply

    except:
        return "idk 😭"

# =========================
# 🚀 MAIN
# =========================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()

    if "shria" not in content and bot.user not in message.mentions:
        return

    # SAY
    if "say" in content:
        word, count = parse_say_command(content)
        if word and count:
            await message.channel.send("uhh bro ok got u 😭")
            repeated = " ".join([word] * count)
            await message.channel.send(repeated)
            return

    # DATE
    if "date" in content or "today" in content:
        await message.channel.send(f"today is {get_today()} 👀")
        return

    # WEATHER
    if "weather" in content or "temperature" in content:
        temp, desc = await get_india_weather()
        await message.channel.send(f"india rn {temp}, {desc} 👀")
        return

    # GOLD
    if "gold" in content:
        usd = await get_gold_price()
        inr = await usd_to_inr(usd)
        await message.channel.send(f"gold rn ${usd} (~₹{inr}) 👀")
        return

    # SILVER
    if "silver" in content:
        usd = await get_silver_price()
        inr = await usd_to_inr(usd)
        await message.channel.send(f"silver rn ${usd} (~₹{inr}) 👀")
        return

    # STOCK
    for key in STOCKS:
        if key in content:
            name, price = await get_stock_price(STOCKS[key])
            if price:
                await message.channel.send(f"{name} rn ₹{price} 👀")
            else:
                await message.channel.send("market closed rn 💀")
            return

    # RECIPE
    if is_serious_question(content):
        recipe = get_simple_recipe(content)
        if recipe:
            await message.channel.send(recipe)
            return

    # GIF
    for action in ACTIONS:
        if action in content:
            gif = await get_gif(action)
            if gif:
                await message.channel.send(gif)
            return

    # AI
    reply = await get_ai_reply(message.content)
    await message.channel.send(reply)

bot.run(TOKEN)
