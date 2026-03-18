async def get_reply(user_id, user_message):
    try:
        memory = load_memory()

        user_data = memory.get(str(user_id), {
            "history": [],
            "mood": "neutral",
            "jealousy": 0
        })

        # jealousy
        if any(word in user_message.lower() for word in ["girl","her","she","gf","crush","babe"]):
            user_data["jealousy"] += 1
        else:
            user_data["jealousy"] = max(0, user_data["jealousy"] - 1)

        if user_data["jealousy"] >= 3:
            user_data["mood"] = "jealous"

        mood = user_data["mood"]

        # 🔥 NEW HUMAN PROMPT
        system_prompt = (
            "You are Shria, a real Discord girl.\n"
            
            "IMPORTANT RULES:\n"
            "- Talk like real person, not AI\n"
            "- Keep replies VERY SHORT (1–5 words mostly)\n"
            "- DO NOT always answer directly\n"
            "- Sometimes dodge questions\n"
            "- Sometimes ask back\n"
            "- Sometimes just react (like 'idk', 'bruh', 'huh?')\n"
            "- Don't overuse slang\n"
            "- No cringe lines\n"
            "- Be slightly playful or teasing\n"
            
            "Examples:\n"
            "User: do you like coffee?\n"
            "Reply: ehh sometimes\n"
            
            "User: what?\n"
            "Reply: nothing 😭\n"
            
            "User: are you mad?\n"
            "Reply: maybe 👀\n"
        )

        messages = [{"role": "system", "content": system_prompt}]
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
                    "temperature": 1.5
                }
            ) as res:
                data = await res.json()

        reply = data["choices"][0]["message"]["content"].strip()

        # 🔥 HUMAN RANDOMIZER
        if random.random() < 0.3:
            reply = random.choice([
                "idk 😭",
                "huh?",
                "bruhh",
                "maybe 👀",
                "nah",
                "ehh",
                "what"
            ])

        # shorten hard
        reply = reply.split("\n")[0][:60]

        memory[str(user_id)] = user_data
        save_memory(memory)

        return reply

    except Exception as e:
        print(e)
        return random.choice(["idk 😭", "bruhh", "nah"])
