import discord
import wavelink
import requests
import asyncio
import random
import os

# =========================
# 🔐 Environment Variables
# =========================
TOKEN = os.getenv("TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")

# =========================
# ⚙️ Discord Setup
# =========================
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

client = discord.Client(intents=intents)

# =========================
# 🎌 Action Commands
# =========================
ACTIONS = ["kiss", "hug", "slap", "punch", "kick", "cry", "blush", "laugh"]


# =========================
# 🎬 Fetch Anime GIF
# =========================
def get_gif(action: str):
    try:
        url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q=anime+{action}&limit=20"
        response = requests.get(url).json()

        gifs = [g["images"]["original"]["url"] for g in response["data"]]

        return random.choice(gifs) if gifs else None
    except Exception:
        return None


# =========================
# 💬 AI Response (Groq)
# =========================
def get_reply(user_message: str):
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are Shria, cute, flirty, short replies, playful personality.",
                    },
                    {"role": "user", "content": user_message},
                ],
                "temperature": 1.1,
            },
        )

        return response.json()["choices"][0]["message"]["content"]

    except Exception:
        return "ugh my brain lagged 😭"


# =========================
# 🎵 Get / Create Player
# =========================
async def get_player(message):
    if not message.author.voice or not message.author.voice.channel:
        await message.channel.send("Join a voice channel first 😭")
        return None

    voice_channel = message.author.voice.channel
    vc: wavelink.Player = message.guild.voice_client

    # Always reconnect cleanly (avoids broken sessions)
    if vc:
        try:
            await vc.disconnect()
        except Exception:
            pass

    vc = await voice_channel.connect(cls=wavelink.Player)
    await asyncio.sleep(0.5)

    return vc


# =========================
# 🎵 Play Music
# =========================
async def play_music(message, query: str):
    vc = await get_player(message)
    if not vc:
        return

    search_query = query if query.startswith("http") else f"ytsearch:{query}"

    try:
        tracks = await wavelink.Playable.search(search_query)
    except Exception as e:
        print("Search error:", e)
        await message.channel.send("Couldn't search for that 😭")
        return

    if not tracks:
        await message.channel.send("No results found 😭")
        return

    track = tracks[0]

    try:
        await vc.play(track)
    except Exception as e:
        print("Play error:", e)
        await message.channel.send("Music failed to play 😭")
        return

    print(f"🎵 Playing: {track.title}")
    print(f"🔊 Status: {vc.playing}")

    await message.channel.send(f"🎶 Playing: **{track.title}**")


# =========================
# 🔌 Lavalink Setup
# =========================
@client.event
async def on_ready():
    node = wavelink.Node(
        uri="http://lavalink.oops.wtf:80",
        password="oops"
    )

    await wavelink.Pool.connect(client=client, nodes=[node])

    print(f"💖 Logged in as {client.user}")


# =========================
# 🎵 Debug Events
# =========================
@client.event
async def on_wavelink_track_start(payload):
    print(f"🎵 Track started: {payload.track.title}")


@client.event
async def on_wavelink_track_end(payload):
    print(f"🔚 Track ended: {payload.reason}")


@client.event
async def on_wavelink_track_exception(payload):
    print(f"❌ Track error: {payload.exception}")


# =========================
# 💬 Main Message Handler
# =========================
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content.lower()

    # =====================
    # 🎵 Music Commands
    # =====================
    if content.startswith("/play"):
        query = message.content[5:].strip()
        await play_music(message, query)
        return

    if content.startswith("/skip"):
        vc = message.guild.voice_client
        if vc and vc.playing:
            await vc.skip()
            await message.channel.send("⏭️ Skipped")
        else:
            await message.channel.send("Nothing playing 😭")
        return

    if content.startswith("/pause"):
        vc = message.guild.voice_client
        if vc:
            await vc.pause(not vc.paused)
            await message.channel.send("⏸️ Paused" if vc.paused else "▶️ Resumed")
        return

    if content.startswith("/stop"):
        vc = message.guild.voice_client
        if vc:
            await vc.stop()
            await message.channel.send("⏹️ Stopped")
        return

    if content.startswith("/leave"):
        vc = message.guild.voice_client
        if vc:
            await vc.disconnect()
            await message.channel.send("👋 Left VC")
        return

    # =====================
    # 🎬 Action Commands
    # =====================
    if "shria" not in content and client.user not in message.mentions:
        return

    for action in ACTIONS:
        if action in content:
            gif = get_gif(action)

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
    # 💬 AI Chat
    # =====================
    await message.channel.typing()
    await asyncio.sleep(0.5)

    reply = get_reply(message.content)
    await message.channel.send(reply)


# =========================
# 🚀 Start Bot
# =========================
client.run(TOKEN)