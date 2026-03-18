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
    return datetime.now().strftime("%A, %d %B %Y")

# =========================
# 🌡️ WEATHER
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
            return f"Delhi rn {temp}, {desc} 🌤️"
    except:
        pass

    return random.choice([
        "kinda warm rn 😏",
        "hot outside fr ☀️",
        "weather chill rn 👀"
    ])

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
# 💋 EMOJI SYSTEM
# =========================
def pick_emoji(msg):
    if "love" in msg:
        return random.choice(["❤️","😘","😏"])
    if "funny" in msg:
        return random.choice(["😂","🤣","💀"])
    return random.choice(["😏","👀","😂","💀"])

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
                         "You are Sky, a flirty, fun, real discord girl. Keep replies natural."},
                        {"role": "user", "content": msg}
                    ]
                }
            ) as res:
                data = await res.json()

        reply = data["choices"][0]["message"]["content"].split("\n")[0][:100]
        return f"{reply} {pick_emoji(reply)}"

    except:
        return f"idk but you're kinda cute {pick_emoji(msg)}"

# =========================
# 🚀 MAIN
# =========================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()

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
        "sky" in content or
        bot.user in message.mentions or
        is_reply
    )

    if not trigger:
        return

    # 📢 TAG EVERYONE
    if "tag everyone" in content:
        await message.channel.send(
            "@everyone wake up 👀",
            allowed_mentions=discord.AllowedMentions(everyone=True)
        )
        return

    # 🔁 SAY
    text, count = parse_say(content)
    if text:
        await message.channel.send("ok fine 😭")
        await message.channel.send(" ".join([text]*count))
        return

    # 🌡️ WEATHER
    if "temp" in content or "weather" in content:
        await message.channel.send(await get_weather())
        return

    # 📅 DATE
    if "date" in content:
        await message.channel.send(get_today())
        return

    # 🎬 GIF
    for a in ACTIONS:
        if a in content:
            gif = await get_gif(a)
            if gif:
                await message.channel.send(gif)
            return

    # 💬 AI
    reply = await ai_reply(message.content)
    await message.channel.send(reply)

bot.run(TOKEN)
