import discord
import requests
import asyncio
import random
import os
import yt_dlp
from discord import FFmpegPCMAudio

# =========================
# 🔐 ENV VARIABLES
# =========================
TOKEN = os.getenv("TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")

# =========================
# ⚙️ DISCORD SETUP
# =========================
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

client = discord.Client(intents=intents)

# =========================
# 🎌 ACTIONS
# =========================
ACTIONS = ["kiss", "hug", "slap", "punch", "kick", "cry", "blush", "laugh"]

# =========================
# 🎬 GIF FETCH
# =========================
def get_gif(action):
    try:
        url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q=anime+{action}&limit=25"
        data = requests.get(url).json()
        gifs = [g["images"]["original"]["url"] for g in data["data"]]
        return random.choice(gifs) if gifs else None
    except:
        return None

# =========================
# 💬 AI REPLY
# =========================
def get_reply(msg):
    try:
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "You are Shria, cute, flirty, playful."},
                    {"role": "user", "content": msg},
                ],
            },
        )
        return res.json()["choices"][0]["message"]["content"]
    except:
        return "ugh brain lag 😭"

# =========================
# 🎵 MUSIC (NO LAVALINK)
# =========================
ytdl = yt_dlp.YoutubeDL({"format": "bestaudio", "quiet": True})

async def play_music(message, query):
    if not message.author.voice:
        await message.channel.send("Join VC first 😭")
        return

    channel = message.author.voice.channel
    vc = message.guild.voice_client

    if not vc:
        vc = await channel.connect()

    if not query.startswith("http"):
        query = f"ytsearch:{query}"

    info = ytdl.extract_info(query, download=False)

    if "entries" in info:
        info = info["entries"][0]

    url = info["url"]
    title = info["title"]

    vc.stop()
    vc.play(FFmpegPCMAudio(url))

    await message.channel.send(f"🎶 Playing: {title}")

# =========================
# 💬 EVENTS
# =========================
@client.event
async def on_ready():
    print(f"💖 Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content.lower()

    # 🎵 MUSIC COMMANDS
    if content.startswith("/play"):
        query = message.content[5:].strip()
        await play_music(message, query)
        return

    if content.startswith("/stop"):
        vc = message.guild.voice_client
        if vc:
            await vc.disconnect()
            await message.channel.send("👋 Left VC")
        return

    # 🎬 ACTIONS
    if "shria" not in content and client.user not in message.mentions:
        return

    for action in ACTIONS:
        if action in content:
            gif = get_gif(action)

            text = f"{message.author.mention} {action}ed someone 😭"
            embed = discord.Embed(description=text)

            if gif:
                embed.set_image(url=gif)

            await message.channel.send(embed=embed)
            return

    # 💬 AI CHAT
    await message.channel.typing()
    await asyncio.sleep(0.5)

    reply = get_reply(message.content)
    await message.channel.send(reply)

# =========================
# 🚀 RUN
# =========================
client.run(TOKEN)
