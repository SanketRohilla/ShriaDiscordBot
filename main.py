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
def get_gif(action):
    try:
        url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q=anime+{action}&limit=25"
        res = requests.get(url).json()
        gifs = [g["images"]["original"]["url"] for g in res["data"]]
        return random.choice(gifs) if gifs else None
    except:
        return None


# =========================
# 💬 AI Response
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
                    {"role": "system", "content": "You are Shria, cute, flirty, short replies."},
                    {"role": "user", "content": msg},
                ],
            },
        )
        return res.json()["choices"][0]["message"]["content"]
    except:
        return "ugh brain lag 😭"


# =========================
# 🎵 Player Setup
# =========================
async def get_player(message):
    if not message.author.voice:
        await message.channel.send("Join VC first 😭")
        return None

    voice_channel = message.author.voice.channel
    vc: wavelink.Player = message.guild.voice_client

    if not vc:
        vc = await voice_channel.connect(cls=wavelink.Player)
    elif vc.channel != voice_channel:
        await vc.move_to(voice_channel)

    return vc


# =========================
# 🎵 Play Music
# =========================
async def play_music(message, query):
    vc = await get_player(message)
    if not vc:
        return

    search = query if query.startswith("http") else f"ytsearch:{query}"

    tracks = await wavelink.Playable.search(search)

    if not tracks:
        await message.channel.send("No results 😭")
        return

    track = tracks[0]

    await vc.play(track)

    print(f"🎵 Playing: {track.title}")
    await message.channel.send(f"🎶 Playing: **{track.title}**")


# =========================
# 🔌 Lavalink Setup (FIXED)
# =========================
@client.event
async def on_ready():
    nodes = [
        wavelink.Node(uri="http://lava.link:80", password="anything"),
        wavelink.Node(uri="http://lavalinkv4.serenetia.com:80", password="https://seretia.link/discord"),
        wavelink.Node(uri="http://n3.nexcloud.in:2026", password="nexcloud"),
    ]

    await wavelink.Pool.connect(client=client, nodes=nodes)

    print(f"💖 Logged in as {client.user}")


# =========================
# 🎵 Debug Logs
# =========================
@client.event
async def on_wavelink_node_ready(payload):
    print(f"✅ Connected: {payload.node.uri}")


@client.event
async def on_wavelink_track_start(payload):
    print(f"🎵 Started: {payload.track.title}")


@client.event
async def on_wavelink_track_exception(payload):
    print(f"❌ Error: {payload.exception}")


# =========================
# 💬 Main Handler
# =========================
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content.lower()

    # 🎵 MUSIC
    if msg.startswith("/play"):
        query = message.content[5:].strip()
        await play_music(message, query)
        return

    if msg.startswith("/skip"):
        vc = message.guild.voice_client
        if vc:
            await vc.skip()
        return

    if msg.startswith("/pause"):
        vc = message.guild.voice_client
        if vc:
            await vc.pause(not vc.paused)
        return

    if msg.startswith("/stop"):
        vc = message.guild.voice_client
        if vc:
            await vc.stop()
        return

    if msg.startswith("/leave"):
        vc = message.guild.voice_client
        if vc:
            await vc.disconnect()
        return

    # 🎬 ACTIONS
    if "shria" not in msg and client.user not in message.mentions:
        return

    for action in ACTIONS:
        if action in msg:
            gif = get_gif(action)

            text = f"{message.author.mention} {action}ed someone 😭"
            if message.mentions:
                text = f"{message.author.mention} {action}ed {message.mentions[0].mention} 😭"

            embed = discord.Embed(description=text)
            if gif:
                embed.set_image(url=gif)

            await message.channel.send(embed=embed)
            return

    # 💬 AI
    await message.channel.typing()
    await asyncio.sleep(0.5)

    reply = get_reply(message.content)
    await message.channel.send(reply)


# =========================
# 🚀 Run
# =========================
client.run(TOKEN)
