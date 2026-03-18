import discord
import random
import aiohttp
import os
from datetime import datetime
from discord.ext import commands

TOKEN = os.getenv("TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="", intents=intents)

active_users = {}

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
    return datetime.now().strftime("%A, %d %B %Y")

# =========================
# 🌡️ WEATHER (FIXED HARD)
# =========================
async def get_weather():
    try:
        url = "https://goweather.herokuapp.com/weather/Delhi"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as res:
                data = await res.json()

        temp = data.get("temperature")
        desc = data.get("description")

        if temp:
            return f"Delhi rn {temp}, {desc} 👀"

    except:
        pass

    # fallback ALWAYS
    return random.choice([
        "Delhi rn around 30°C kinda warm 😭",
        "prob like 28-32°C rn 👀",
        "lowkey hot outside ngl ☀️"
    ])

# =========================
# 💰 GOLD / SILVER
# =========================
async def get_price(metal):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.gold-api.com/price/{metal}") as res:
                data = await res.json()

        usd = data["price"]

        async with aiohttp.ClientSession() as session:
            async with session.get("https://open.er-api.com/v6/latest/USD") as res:
                rate = (await res.json())["rates"]["INR"]

        return f"${usd} (~₹{round(usd*rate,2)})"
    except:
        return None

# =========================
# 📈 STOCK
# =========================
STOCKS = {
    "infosys": "INFY.NS",
    "tcs": "TCS.NS",
    "reliance": "RELIANCE.NS",
    "hdfc": "HDFCBANK.NS"
}

async def get_stock(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                data = await res.json()

        result = data["quoteResponse"]["result"]
        if not result:
            return None

        return f"{result[0]['shortName']} rn ₹{result[0]['regularMarketPrice']} 📈"
    except:
        return None

# =========================
# 🍳 RECIPE
# =========================
def get_recipe(msg):
    if "cake" in msg:
        return "cake:\n1 mix flour sugar eggs\n2 add milk butter\n3 bake 180C 🍰"
    if "tea" in msg:
        return "tea:\n1 boil water\n2 add tea milk\n3 sugar ☕"
    if "bread" in msg:
        return "bread:\n1 flour yeast\n2 knead\n3 bake 🍞"
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
# 🎭 SMART EMOJI SYSTEM
# =========================
def pick_emoji(msg):
    msg = msg.lower()

    if "lol" in msg or "funny" in msg:
        return random.choice(["😂","🤣","💀"])

    if "love" in msg or "cute" in msg:
        return random.choice(["❤️","😏","😘"])

    if "angry" in msg or "mad" in msg:
        return random.choice(["😤","💢","😒"])

    if "money" in msg or "stock" in msg:
        return random.choice(["💸","📈","🤑"])

    if "weather" in msg or "temp" in msg:
        return random.choice(["☀️","🌡️","🌤️"])

    return random.choice(["😭","👀","😏","💀","😂"])

# =========================
# 💬 AI
# =========================
async def ai_reply(msg):
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
                        {"role": "system", "content":
                         "You are Shria, a funny, flirty, real discord girl. Be helpful when needed."},
                        {"role": "user", "content": msg}
                    ]
                }
            ) as res:
                data = await res.json()

        reply = data["choices"][0]["message"]["content"].split("\n")[0][:100]

        emoji = pick_emoji(reply)
        return f"{reply} {emoji}"

    except:
        return f"idk {pick_emoji(msg)}"

# =========================
# 🚀 MAIN
# =========================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()
    user_id = message.author.id

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
        "shria" in content or
        bot.user in message.mentions or
        is_reply or
        active_users.get(user_id)
    )

    if not trigger:
        return

    active_users[user_id] = True

    if "bye" in content:
        active_users[user_id] = False

    # SAY
    text, count = parse_say(content)
    if text:
        await message.channel.send(f"okok chill {pick_emoji(content)}")
        await message.channel.send(" ".join([text]*count))
        return

    # WEATHER
    if "temp" in content or "weather" in content:
        await message.channel.send(await get_weather())
        return

    # DATE
    if "date" in content:
        await message.channel.send(get_today())
        return

    # GOLD
    if "gold" in content:
        p = await get_price("XAU")
        await message.channel.send(f"gold rn {p}" if p else "error 💀")
        return

    # SILVER
    if "silver" in content:
        p = await get_price("XAG")
        await message.channel.send(f"silver rn {p}" if p else "error 💀")
        return

    # STOCK
    for key in STOCKS:
        if key in content:
            res = await get_stock(STOCKS[key])
            await message.channel.send(res if res else "market weird rn 💀")
            return

    # RECIPE
    if "how to" in content or "make" in content:
        r = get_recipe(content)
        if r:
            await message.channel.send(r)
            return

    # GIF
    for a in ACTIONS:
        if a in content:
            gif = await get_gif(a)
            if gif:
                await message.channel.send(gif)
            return

    # AI
    reply = await ai_reply(message.content)
    await message.channel.send(reply)

bot.run(TOKEN)
