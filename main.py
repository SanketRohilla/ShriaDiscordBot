import discord
import random
import requests
import yt_dlp
import asyncio
import os

from discord.ext import commands

# ===== CONFIG =====
TOKEN = os.getenv("TOKEN")
GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ===== BOT SETUP =====
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="", intents=intents)

# ===== YTDL SETUP =====
ytdl = yt_dlp.YoutubeDL({
    'format': 'bestaudio/best',
    'quiet': True,
    'noplaylist': True,
})

# ===== READY =====
@bot.event
async def on_ready():
    print(f"💖 Logged in as {bot.user}")

# ===== GIF FUNCTION =====
def get_gif(action):
    url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q=anime {action}&limit=25"
    data = requests.get(url).json()
    gifs = [g['images']['original']['url'] for g in data['data']]
    return random.choice(gifs) if gifs else None

# ===== AUDIO FETCH =====
async def get_audio_url(query):
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(
        None,
        lambda: ytdl.extract_info(f"ytsearch:{query}", download=False)
    )
    return data['entries'][0]['url']

# ===== MAIN MESSAGE HANDLER =====
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()

    # ===== GIF COMMANDS =====
    actions = ["slap", "kiss", "hug", "kick", "cry", "blush", "laugh"]
    for action in actions:
        if action in content:
            gif = get_gif(action)
            if gif:
                await message.channel.send(f"{message.author.mention} {action}s someone 💖\n{gif}")
            return

    # ===== MUSIC PLAY =====
    if content.startswith("/play"):
        query = message.content.replace("/play", "").strip()

        if not message.author.voice:
            await message.channel.send("❌ Join VC first")
            return

        channel = message.author.voice.channel
        vc = discord.utils.get(bot.voice_clients, guild=message.guild)

        if not vc:
            vc = await channel.connect(reconnect=True)
        else:
            await vc.move_to(channel)

        await message.channel.send(f"🎶 Playing: {query}")

        try:
            url = await get_audio_url(query)
        except:
            await message.channel.send("❌ Error fetching song")
            return

        if vc.is_playing():
            vc.stop()

        source = discord.FFmpegPCMAudio(
            url,
            executable="ffmpeg"
        )

        vc.play(source)

    # ===== STOP =====
    elif content.startswith("/stop"):
        vc = discord.utils.get(bot.voice_clients, guild=message.guild)
        if vc:
            await vc.disconnect()
            await message.channel.send("⏹️ Stopped")

    # ===== AI CHAT (GROQ) =====
    else:
        try:
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }

            json_data = {
                "model": "mixtral-8x7b-32768",
                "messages": [{"role": "user", "content": message.content}]
            }

            res = requests.post("https://api.groq.com/openai/v1/chat/completions",
                                headers=headers, json=json_data)

            reply = res.json()["choices"][0]["message"]["content"]
            await message.channel.send(reply)

        except:
            pass

# ===== RUN =====
bot.run(TOKEN)
