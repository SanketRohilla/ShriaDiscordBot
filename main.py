import discord
import random
import aiohttp
import asyncio
import os
import json

from discord.ext import commands

TOKEN = os.getenv("TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="", intents=intents)

# =========================
# 💾 MEMORY SYSTEM
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
# 🎬 GIF
# =========================
async def get_gif(action):
    try:
        url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q=anime+{action}&limit=25"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                data = await res.json()

        gifs = [g["images"]["original"]["url"] for g in data["data"]]
        return random.choice(gifs) if gifs else None
    except:
        return None

# =========================
# 😏 SMART REPLIES
# =========================
def smart_reply(msg):
    msg = msg.lower()

    if "good" in msg or "nice" in msg:
        return random.choice([
            "oh nice, what happened?",
            "good how? tell me 👀",
            "hmm sounds interesting"
        ])

    if "arrest" in msg or "jail" in msg:
        return random.choice([
            "wait what did I do 😭",
            "nahhh I’m innocent fr",
            "you setting me up 💀"
        ])

    if "baby" in msg:
        return random.choice([
            "huh? who u calling that 😭",
            "careful with that word 😏",
            "you getting bold now huh"
        ])

    return None

# =========================
# 💬 AI WITH MEMORY
# =========================
async def get_ai_reply(user_id, user_message):
    memory = load_memory()

    user_data = memory.get(str(user_id), {
        "history": []
    })

    history = user_data["history"][-6:]

    system_prompt = (
        "You are Shria, a friendly, funny, slightly flirty girl.\n"
        "- Talk like a real human\n"
        "- Keep conversation flowing\n"
        "- Ask questions sometimes\n"
        "- React naturally\n"
        "- Be playful and fun\n"
        "- Do NOT act like AI\n"
        "- You prefer tea, not coffee\n"
    )

    messages = [{"role": "system", "content": system_prompt}]

    for msg in history:
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
    user_data["history"].append({"role": "user", "content": user_message})
    user_data["history"].append({"role": "assistant", "content": reply})

    memory[str(user_id)] = user_data
    save_memory(memory)

    return reply.split("\n")[0][:120]

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
    if "hug" in content or "kiss" in content:
        gif = await get_gif("hug")
        if gif:
            await message.channel.send(gif)
        return

    # SMART REPLY FIRST
    smart = smart_reply(content)
    if smart:
        await message.channel.send(smart)
        return

    # AI
    await message.channel.typing()
    await asyncio.sleep(random.uniform(0.5, 1.0))

    reply = await get_ai_reply(message.author.id, message.content)
    await message.channel.send(reply)

bot.run(TOKEN)
