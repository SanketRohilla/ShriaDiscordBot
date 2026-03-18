import discord
from discord.ext import commands
import wavelink

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.setup_nodes())

    async def setup_nodes(self):
        await self.bot.wait_until_ready()

        try:
            await wavelink.Pool.connect(
                nodes=[
                    wavelink.Node(
                        uri="https://lavalink-2026-production-536b.up.railway.app",
                        password="mysuperpass"
                    )
                ],
                client=self.bot
            )
            print("✅ Lavalink connected!")
        except Exception as e:
            print(f"❌ Lavalink error: {e}")

    # =========================
    # 🎵 PLAY (pl)
    # =========================
    @commands.command(name="pl")
    async def play(self, ctx, *, search: str):
        if not ctx.author.voice:
            return await ctx.send("Join VC first 😭")

        vc: wavelink.Player = (
            ctx.voice_client or
            await ctx.author.voice.channel.connect(cls=wavelink.Player)
        )

        tracks = await wavelink.Playable.search(f"ytsearch:{search}")

         print("TRACKS FOUND:", tracks)

        if not tracks:
            return await ctx.send("No results 💀")

        track = tracks[0]

        if vc.playing:
            await vc.queue.put(track)
            await ctx.send(f"📝 Added **{track.title}**")
        else:
            await vc.play(track)
            await ctx.send(f"🎶 Playing **{track.title}**")

    # =========================
    # ⏭️ SKIP (sk)
    # =========================
    @commands.command(name="sk")
    async def skip(self, ctx):
        vc: wavelink.Player = ctx.voice_client

        if vc and vc.playing:
            await vc.skip()
            await ctx.send("⏭️ Skipped")
        else:
            await ctx.send("Nothing playing ❌")

    # =========================
    # ⏸️ PAUSE (ps)
    # =========================
    @commands.command(name="ps")
    async def pause(self, ctx):
        vc: wavelink.Player = ctx.voice_client

        if vc and vc.playing:
            await vc.pause(True)
            await ctx.send("⏸️ Paused")
        else:
            await ctx.send("Nothing playing ❌")

    # =========================
    # ▶️ RESUME (rs)
    # =========================
    @commands.command(name="rs")
    async def resume(self, ctx):
        vc: wavelink.Player = ctx.voice_client

        if vc and vc.paused:
            await vc.pause(False)
            await ctx.send("▶️ Resumed")
        else:
            await ctx.send("Nothing paused ❌")

    # =========================
    # 🛑 STOP (st)
    # =========================
    @commands.command(name="st")
    async def stop(self, ctx):
        vc: wavelink.Player = ctx.voice_client

        if vc:
            await vc.disconnect()
            await ctx.send("👋 Left VC")
        else:
            await ctx.send("Not in VC ❌")

    # =========================
    # 📜 QUEUE (q)
    # =========================
    @commands.command(name="q")
    async def queue(self, ctx):
        vc: wavelink.Player = ctx.voice_client

        if not vc or vc.queue.is_empty:
            return await ctx.send("Queue empty 💀")

        upcoming = list(vc.queue)[:5]
        desc = "\n".join(f"{i+1}. {t.title}" for i, t in enumerate(upcoming))

        await ctx.send(f"🎶 Queue:\n{desc}")

    # =========================
    # 🔊 VOLUME (vol)
    # =========================
    @commands.command(name="vol")
    async def volume(self, ctx, vol: int):
        vc: wavelink.Player = ctx.voice_client

        if not vc:
            return await ctx.send("Not in VC ❌")

        vol = max(0, min(vol, 100))
        await vc.set_volume(vol)

        await ctx.send(f"🔊 Volume: {vol}%")

async def setup(bot):
    await bot.add_cog(Music(bot))
