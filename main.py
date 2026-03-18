import discord
import random
import aiohttp
import asyncio
import os
import json

from discord.ext import commands

# =========================
# 🔐 ENV
# =========================
TOKEN = os.getenv("TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")

# =========================
# ⚙️ BOT
# =========================
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
# 🎬 GIF SYSTEM
# =========================
gif_cache = {}

ACTIONS = [
    "kiss","hug","slap","punch","kick",
    "cry","blush","laugh","pat","cuddle"
]

async def get_gif(action):
    try:
        url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q=anime+{action}&limit=50"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                data = await res.json()

        gifs = [g["images"]["original"]["url"] for g in data["data"]]

        if not gifs:
            return None

        if action not in gif_cache:
            gif_cache[action] = []

        available = list(set(gifs) - set(gif_cache[action]))

        if not available:
            gif_cache[action] = []
            available = gifs

        gif = random.choice(available)
        gif_cache[action].append(gif)

        return gif

    except:
        return None

# =========================
# 😏 SMART HUMAN RESPONSES
# =========================
def smart_reply(msg):
    msg = msg.lower()

    if "5 feet" in msg or "short" in msg:
        return random.choice([
            "wow okay 😭 but I still carry myself better than you",
            "so what? I like it that way",
            "short but still winning 👀"
        ])

    if "dumb" in msg:
        return random.choice([
            "wow rude 😭",
            "nah you just mad",
            "look who’s talking"
        ])

    if "coffee" in msg:
        return random.choice([
            "nahh not really, I prefer tea",
            "green tea over coffee any day",
            "coffee’s not really my thing"
        ])

    return None

# =========================
# 💬 AI (NORMAL + FLIRTY)
# =========================
async def get_ai_reply(user_message):
    try:
        system_prompt = (
            "You are Shria, a friendly, slightly flirty girl chatting naturally.\n"
            "- Talk like a real human\n"
            "- Keep replies normal length (1–2 sentences)\n"
            "- Be playful and slightly teasing\n"
            "- Keep conversation flowing\n"
            "- Do NOT act like AI\n"
            "- No cringe lines\n"
            "- You do NOT like coffee, you prefer tea or green tea\n"
        )

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
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "temperature": 1.1
                }
            ) as res:
                data = await res.json()

        reply = data["choices"][0]["message"]["content"]
        return reply.split("\n")[0][:120]

    except:
        return random.choice([
            "hmm I don’t know 😭",
            "you’re confusing me",
            "wait what 😭"
        ])

# =========================
# 🚀 READY
# =========================
@bot.event
async def on_ready():
    print(f"💖 Logged in as {bot.user}")

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

    # GIF
    for action in ACTIONS:
        if action in content:
            gif = await get_gif(action)
            embed = discord.Embed(description=f"{message.author.mention} {action}ed someone 💖")
            if gif:
                embed.set_image(url=gif)
            await message.channel.send(embed=embed)
            return

    # SMART REPLY FIRST
    reply = smart_reply(content)
    if reply:
        await message.channel.send(reply)
        return

    # AI
    await message.channel.typing()
    await asyncio.sleep(random.uniform(0.4, 0.8))

    reply = await get_ai_reply(message.content)
    await message.channel.send(reply)

# =========================
# ▶️ RUN
# =========================
bot.run(TOKEN)
