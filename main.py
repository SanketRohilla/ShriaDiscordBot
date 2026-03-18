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
# 💾 MEMORY FILE
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
# 🎬 GIF CACHE (NO REPEAT)
# =========================
gif_cache = {}

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

        # remove used gifs
        available = list(set(gifs) - set(gif_cache[action]))

        if not available:
            gif_cache[action] = []
            available = gifs

        gif = random.choice(available)
        gif_cache[action].append(gif)

        return gif

    except Exception as e:
        print("GIF ERROR:", e)
        return None

# =========================
# 🎭 TRUTH OR DARE
# =========================
TRUTHS = [
    "what's your biggest secret 👀",
    "who do you like rn be honest 😏",
    "last lie you told?",
    "biggest fear?"
]

DARES = [
    "text someone 'i miss you' 😭",
    "say something cringe in chat",
    "send last emoji you used",
    "compliment someone random"
]

# =========================
# 💬 AI
# =========================
async def get_reply(user_id, user_message):
    try:
        memory = load_memory()

        user_data = memory.get(str(user_id), {})
        past = user_data.get("history", [])[-3:]

        system_prompt = (
            "You are Shria, a playful, flirty (but safe), female anime friend. "
            "You talk like a chill friend using words like 'dang', 'lol', 'bruhh'. "
            "Keep replies SHORT (1 sentence max). "
            "No long explanations. No coffee talk unless asked. "
            "Be slightly teasing, fun, and friendly. "
            "Never be adult or explicit. Keep it safe."
        )

        messages = [{"role": "system", "content": system_prompt}]

        for msg in past:
            messages.append(msg)

        messages.append({"role": "user", "content": user_message})

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": messages,
                    "temperature": 1.2
                }
            ) as res:
                data = await res.json()

        reply = data["choices"][0]["message"]["content"]

        # SAVE MEMORY
        memory.setdefault(str(user_id), {"history": []})
        memory[str(user_id)]["history"].append({"role": "user", "content": user_message})
        memory[str(user_id)]["history"].append({"role": "assistant", "content": reply})

        save_memory(memory)

        return reply

    except Exception as e:
        print("AI ERROR:", e)
        return "bruhh my brain froze 😭"

# =========================
# 🎌 ACTIONS
# =========================
ACTIONS = ["kiss", "hug", "slap", "punch", "kick", "cry", "blush", "laugh"]

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

    # =====================
    # 🎭 TRUTH / DARE
    # =====================
    if "truth" in content:
        await message.channel.send(random.choice(TRUTHS))
        return

    if "dare" in content:
        await message.channel.send(random.choice(DARES))
        return

    # =====================
    # 🎬 GIF ACTIONS
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
    # 💬 AI CHAT
    # =====================
    try:
        await message.channel.typing()
        await asyncio.sleep(0.3)

        reply = await get_reply(message.author.id, message.content)
        await message.channel.send(reply)

    except Exception as e:
        print("MAIN ERROR:", e)
        await message.channel.send("bruhh something broke 😭")

# =========================
# ▶️ RUN
# =========================
bot.run(TOKEN)
