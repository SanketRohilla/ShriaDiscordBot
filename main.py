import discord
import random
import aiohttp
import os
import re
from discord.ext import commands, tasks

TOKEN = os.getenv("TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="", intents=intents)

# =========================
# 💖 EMOJIS
# =========================
LOVE_EMOJIS = ["❤️","😍","😘","💕","💓","💞","💖","💗","💘"]
DANGER_EMOJIS = ["🔫","🔪","💣","⚔️","🗡️"]

def is_only_emoji(msg):
    return all(char in ''.join(LOVE_EMOJIS + DANGER_EMOJIS) for char in msg)

# =========================
# 💖 LOVE LINES
# =========================
LOVE_LINES = [
    "you looking kinda cute today 😏💕",
    "why you always this fine huh 👀💖",
    "lowkey got a crush on you ngl 😏💘",
    "you just made the chat better ✨💕",
    "you really think i wouldn’t notice you? 😏",
"why you looking this good today huh 👀",
"stop… you’re making this unfair for others 😭",
"i swear you just walked in and raised the vibe ✨",
"lowkey been watching you… don’t ask why 😏",
"you got that ‘main character’ energy ngl 💖",
"why you always this attractive bro 😭",
"you just made my mood better for no reason 💕",
"i see you… and yeah, i like that 👀",
"you got that calm but dangerous vibe 😏",
"not even gonna lie… you look kinda perfect rn 💘",
"why you acting cute without permission 😭",
"you walked in like you own the place… and i respect it 😏",
"i don’t chase… but for you i might consider 👀",
"you got me paying attention without even trying 💕",
"you’re the type people don’t forget easily 😏",
"you got that smile that could ruin someone’s focus 😭",
"you really out here making everyone look basic 💀",
"don’t look at me like that… i might fold 😏",
"you just made this chat interesting again ✨",
"you got style… and i like that a lot 💖",
"why you so smooth without trying 😭",
"you just walked in and stole the spotlight 💀",
"you got me curious now… and that’s dangerous 😏",
"you look like trouble… the good kind 👀",
"you really got that rare energy ngl 💕",
"you make boring days feel better 😏",
"i’d pick you over silence any day 💖",
"you got something different… i can’t explain it 😭",
"you really know how to stand out without trying 💀",
"you got me thinking… and that’s risky 😏",
"you just casually being attractive like it’s nothing 😭",
"you got that vibe people can’t copy 💖",
"you really came here just to steal attention huh 👀",
"you got me smiling for no reason 💕",
"you don’t even try and still win 😭",
"you got that calm confidence… dangerous 😏",
"you really built different ngl 💀",
"you just made this place feel alive again ✨",
"you got that ‘i know i’m good’ vibe 😏",
"i don’t compliment people… but you forced it 💖",
"you got me noticing things i shouldn’t 😭",
"you just made everyone else invisible 💀",
"you got that rare mix of chill and attractive 😏",
"you look like someone worth talking to 👀",
"you just changed the whole mood here 💕",
"you got that energy i can’t ignore 😭",
"you really just exist and win 💀",
"you got me lowkey impressed 😏",
"you’re the type people notice instantly 💖",

]

# =========================
# 🔥 ROASTS
# =========================
ROASTS = [
    "bro your brain on airplane mode 💀",
    "npc behavior fr 💀😂",
    "you lag in real life 😭",
    "your iq buffering rn 💀",
    "bro your thoughts buffering rn 💀",
"you typed that and felt smart? 😭",
"you really said that out loud huh 💀",
"npc response detected 😂",
"bro got confidence but no data 💀",
"you the reason tutorials exist 😭",
"your brain running on trial version 💀",
"you really pressed send on that 💀",
"bro your logic took a day off 😂",
"you thinking… but it’s not working 😭",
"you got potential… just not here 💀",
"bro your IQ hiding from you 😂",
"you just surprised yourself with that 💀",
"your brain lagging like bad wifi 😭",
"you really tried… that’s cute 💀",
"bro you thinking in 144p 😂",
"you got ideas… just not good ones 💀",
"you really woke up and chose nonsense 💀",
"bro your logic expired 😭",
"you just embarrassed your keyboard 💀",
"your thoughts need update 😂",
"you really that confident being wrong 💀",
"bro your brain took vacation 😭",
"you typed that with full confidence too 💀",
"your thinking speed negative rn 😂",
"you really that lost? 💀",
"bro you buffering mid sentence 😭",
"you make confusion look easy 💀",
"your logic left the chat 😂",
"you really freestyle nonsense 💀",
"bro your brain running in background 😭",
"you just proved nothing 💀",
"you thought that was it? 😭",
"your ideas need restart 💀",
"bro you glitching in real life 😂",
"you really pressed send like that 💀",
"your thoughts incomplete 😭",
"you talking but not saying anything 💀",
"bro your brain muted 😂",
"you just wasted bandwidth 💀",
"your logic missing 😂",
"you really that confident with zero info 💀",
"bro your IQ hiding 😂",
"you just typed words… not meaning 💀",
"your brain offline rn 😭",
"you tried… but it didn’t work 💀",
"bro your thoughts cancelled 😂",
"you just confused yourself 💀",
"your logic took L 💀",
"you really thought that made sense 😭",
    
]

# =========================
# 😒 JEALOUS
# =========================
JEALOUS_LINES = [
    "oh… so now it's about her? 😒",
    "go talk to her then 🙄",
    "wow… replaced me that fast? 💀",
]

GIRL_WORDS = ["she","her","girl","other girl"]

tagged_users = {}

# =========================
# 📢 FIND MEMBER
# =========================
def find_member(guild, name):
    name = name.lower()
    for m in guild.members:
        if name in m.name.lower() or name in m.display_name.lower():
            return m
    return None

# =========================
# 🍳 RECIPE
# =========================
async def recipe_ai(food):
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {"role":"system","content":"give simple short recipe steps"},
                        {"role":"user","content": f"how to make {food}"}
                    ]
                }
            ) as r:
                data = await r.json()

        return data["choices"][0]["message"]["content"][:200]
    except:
        return "idk 😭"

# =========================
# 🎬 GIF
# =========================
ACTIONS = ["kiss","hug","slap","punch","kick","cry","blush","laugh"]

async def get_gif(action):
    try:
        url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q=anime+{action}&limit=30"
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                data = await r.json()

        gifs = [g["images"]["original"]["url"] for g in data["data"]]
        return random.choice(gifs)
    except:
        return None

# =========================
# 💬 AI
# =========================
async def ai_reply(msg):
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {
                            "role":"system",
                            "content":"You are Sky, flirty and human-like. Always add 1 emoji in reply."
                        },
                        {"role":"user","content": msg}
                    ]
                }
            ) as r:
                data = await r.json()

        return data["choices"][0]["message"]["content"][:120]
    except:
        return "hmm idk 😏"

# =========================
# 💘 COUPLE SYSTEM (FIXED)
# =========================
@tasks.loop(hours=6)
async def couple_loop():
    await bot.wait_until_ready()

    for guild in bot.guilds:
        members = [m for m in guild.members if not m.bot]

        if len(members) < 2:
            continue

        m1, m2 = random.sample(members, 2)

        # find first usable channel
        channel = None
        for ch in guild.text_channels:
            if ch.permissions_for(guild.me).send_messages:
                channel = ch
                break

        if channel:
            await channel.send(
                f"💘 Sky ships {m1.mention} & {m2.mention} now 😏"
            )

# =========================
# 🚀 EVENTS
# =========================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    if not couple_loop.is_running():
        couple_loop.start()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    msg = message.content.strip()
    lower = msg.lower()

    # =====================
    # 💖 EMOJI SYSTEM (FIXED)
    # =====================
    if msg:
        if any(e in msg for e in DANGER_EMOJIS):
            await message.channel.send("why u gonna kill me like that 😭")
            return

        # only emoji message
        if re.fullmatch(r"[^\w\s]+", msg):
            await message.channel.send(random.choice(LOVE_EMOJIS))
            return

    # =====================
    # 🔥 REVENGE ROAST
    # =====================
    if message.author.id in tagged_users:
        await message.channel.send(
            f"{message.author.mention} {random.choice(ROASTS)}"
        )
        tagged_users.pop(message.author.id)
        return

    # =====================
    # TRIGGER
    # =====================
    is_reply = False
    if message.reference:
        try:
            m = await message.channel.fetch_message(message.reference.message_id)
            if m.author == bot.user:
                is_reply = True
        except:
            pass

    trigger = (
        lower.startswith("sky") or
        bot.user in message.mentions or
        is_reply
    )

    if not trigger:
        return

    if lower.startswith("sky"):
        msg = msg[3:].strip()
        lower = msg.lower()

    # jealousy
    if any(w in lower for w in GIRL_WORDS):
        await message.channel.send(random.choice(JEALOUS_LINES))
        return

    # tag
    if "tag" in lower:
        parts = lower.split()

        if "me" in parts:
            user = message.author
        else:
            try:
                name = parts[parts.index("tag")+1]
                user = find_member(message.guild, name)
            except:
                user = None

        if user:
            tagged_users[user.id] = True
            await message.channel.send(
                f"{user.mention} {random.choice(LOVE_LINES)}"
            )
        else:
            await message.channel.send("who even is that 😭")

        return

    # roast
    if "roast" in lower:
        if "everyone" in lower:
            await message.channel.send(
                f"@everyone {random.choice(ROASTS)}",
                allowed_mentions=discord.AllowedMentions(everyone=True)
            )
            return

        if message.mentions:
            u = message.mentions[0]
            await message.channel.send(f"{u.mention} {random.choice(ROASTS)}")
            return

        await message.channel.send(random.choice(ROASTS))
        return

    # recipe
    if "how to make" in lower:
        food = lower.replace("how to make","").strip()
        await message.channel.send(await recipe_ai(food))
        return

    # gif
    for act in ACTIONS:
        if act in lower:
            gif = await get_gif(act)
            if gif:
                await message.channel.send(gif)
            return

    # AI chat
    await message.channel.send(await ai_reply(msg))

bot.run(TOKEN)
