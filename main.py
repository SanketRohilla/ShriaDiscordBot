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
    return now.strftime("%A, %d %B %Y")

# =========================
# 🌡️ WEATHER (FIXED)
# =========================
async def get_weather():
    try:
        url = "https://goweather.herokuapp.com/weather/Delhi"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                data = await res.json()

        temp = data.get("temperature")
        desc = data.get("description")

        if temp:
            return f"india rn {temp}, {desc} 👀"
        else:
            return None
    except:
        return None

# =========================
# 💰 GOLD / SILVER
# =========================
async def get_price(metal):
    try:
        url = f"https://api.gold-api.com/price/{metal}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                data = await res.json()

        usd = data["price"]

        # convert to INR
        async with aiohttp.ClientSession() as session:
            async with session.get("https://open.er-api.com/v6/latest/USD") as res:
                rate = (await res.json())["rates"]["INR"]

        inr = round(usd * rate, 2)
        return f"${usd} (~₹{inr})"
    except:
        return None

# =========================
# 📈 STOCKS
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

        name = result[0]["shortName"]
        price = result[0]["regularMarketPrice"]

        return f"{name} rn ₹{price} 👀"
    except:
        return None

# =========================
# 🍳 RECIPES
# =========================
def get_recipe(msg):
    if "cake" in msg:
        return "cake:\n1 mix flour sugar eggs\n2 add milk butter\n3 bake 180C 🍰"
    if "tea" in msg:
        return "tea:\n1 boil water\n2 add tea milk\n3 sugar ☕"
    if "bread" in msg:
        return "bread:\n1 flour yeast water\n2 knead\n3 bake 🍞"
    return None

# =========================
# 🔁 SAY COMMAND (FIXED)
# =========================
def parse_say(msg):
    words = msg.split()

    if "say" in words or "type" in words:
        try:
            if "say" in words:
                i = words.index("say")
            else:
                i = words.index("type")

            text = words[i+1]

            # handle "20 times"
            if "times" in words:
                count = int(words[i+2])
            else:
                count = int(words[i+2])

            if count > 50:
                count = 50

            return text, count
        except:
            return None, None

    return None, None

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
                        {"role": "system", "content": "short funny genz replies"},
                        {"role": "user", "content": msg}
                    ]
                }
            ) as res:
                data = await res.json()

        reply = data["choices"][0]["message"]["content"][:80]

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

    if "shria" not in content:
        return

    # 🔁 SAY
    text, count = parse_say(content)
    if text and count:
        await message.channel.send("okok chill 😭 here u go")
        await message.channel.send(" ".join([text]*count))
        return

    # 🌡️ WEATHER
    if "temp" in content or "temperature" in content or "weather" in content:
        w = await get_weather()
        if w:
            await message.channel.send(w)
        else:
            await message.channel.send("weather bugging rn 😭")
        return

    # 📅 DATE
    if "date" in content or "today" in content:
        await message.channel.send(get_today())
        return

    # 💰 GOLD
    if "gold" in content:
        p = await get_price("XAU")
        await message.channel.send(f"gold rn {p} 👀" if p else "error 😭")
        return

    # 💰 SILVER
    if "silver" in content:
        p = await get_price("XAG")
        await message.channel.send(f"silver rn {p} 👀" if p else "error 😭")
        return

    # 📈 STOCK
    for key in STOCKS:
        if key in content:
            res = await get_stock(STOCKS[key])
            await message.channel.send(res if res else "market weird rn 💀")
            return

    # 🍳 RECIPE
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
