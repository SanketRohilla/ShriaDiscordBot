import discord
import random
import aiohttp
import asyncio
import os

from discord.ext import commands

# =========================
# 🔐 ENV VARIABLES
# =========================
TOKEN = os.getenv("TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")

# =========================
# ⚙️ BOT SETUP
# =========================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="", intents=intents)

# =========================
# 🎌 ACTIONS
# =========================
ACTIONS = ["kiss", "hug", "slap", "punch", "kick", "cry", "blush", "laugh"]

# =========================
# 🎬 GIF FETCH (LESS REPEAT)
# =========================
async def get_gif(action):
    try:
        url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q=anime+{action}&limit=50"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                data = await res.json()

        gifs = [g["images"]["original"]["url"] for g in data["data"]]

        if gifs:
            random.shuffle(gifs)
            return gifs[0]

        return None

    except Exception as e:
        print("GIF ERROR:", e)
        return None

# =========================
# 💬 AI RESPONSE (GROQ)
# =========================
async def get_reply(user_message):
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        json_data = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {
                    "role": "system",
                    "content": "You are Shria, cute, flirty, funny, playful anime girl. Short replies only."
                },
                {"role": "user", "content": user_message}
            ],
            "temperature": 1.1
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=json_data
            ) as res:
                data = await res.json()

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("AI ERROR:", e)
        return "ugh my brain lagged 😭"

# =========================
# 🚀 READY
# =========================
@bot.event
async def on_ready():
    print(f"💖 Logged in as {bot.user}")

# =========================
# 💬 MAIN HANDLER
# =========================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()

    # =====================
    # 🎬 ACTION GIFS
    # =====================
    for action in ACTIONS:
        if action in content:
            gif = await get_gif(action)

            if message.mentions:
                target = message.mentions[0]
                text = f"{message.author.mention} {action}ed {target.mention} 😭"
            else:
                text = f"{message.author.mention} {action}ed someone 😭"

            embed = discord.Embed(description=text)

            if gif:
                embed.set_image(url=gif)

            await message.channel.send(embed=embed)
            return

    # =====================
    # 💬 AI CHAT (ALWAYS WORKS)
    # =====================
    try:
        await message.channel.typing()
        await asyncio.sleep(0.5)

        reply = await get_reply(message.content)
        await message.channel.send(reply)

    except Exception as e:
        print("MAIN ERROR:", e)
        await message.channel.send("😭 something broke")

# =========================
# ▶️ RUN
# =========================
bot.run(TOKEN)
