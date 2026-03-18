import discord
from discord.ext import commands
import wavelink

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def connect_node(self):
        await self.bot.wait_until_ready()

        try:
            await wavelink.NodePool.create_node(
                bot=self.bot,
                host="lavalink-2026-production-536b.up.railway.app",
                port=443,
                password="mysuperpass",
                https=True
            )
            print("✅ Lavalink connected!")
        except Exception as e:
            print(f"❌ Lavalink error: {e}")

    @commands.Cog.listener()
    async def on_ready(self):
        await self.connect_node()

    # =======================
    # 🎵 PLAY
    # =======================
    @commands.command(name="pl")
    async def play(self, ctx, *, search: str):
        if not ctx.author.voice:
            return await ctx.send("Join VC first 😭")

        vc: wavelink.Player = ctx.voice_client

        if not vc:
            vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)

        tracks = await wavelink.YouTubeTrack.search(search)

        if not tracks:
            return await ctx.send("No results 😭")

        track = tracks[0]

        await vc.play(track)

        await ctx.send(f"🎵 Now playing: **{track.title}**")

    # =======================
    # ⏸ PAUSE
    # =======================
    @commands.command(name="ps")
    async def pause(self, ctx):
        vc = ctx.voice_client
        if vc:
            await vc.pause()
            await ctx.send("Paused ⏸")

    # =======================
    # ▶ RESUME
    # =======================
    @commands.command(name="rs")
    async def resume(self, ctx):
        vc = ctx.voice_client
        if vc:
            await vc.resume()
            await ctx.send("Resumed ▶")

    # =======================
    # ⏹ STOP
    # =======================
    @commands.command(name="st")
    async def stop(self, ctx):
        vc = ctx.voice_client
        if vc:
            await vc.stop()
            await ctx.send("Stopped ⏹")

    # =======================
    # ❌ DISCONNECT
    # =======================
    @commands.command(name="dc")
    async def disconnect(self, ctx):
        vc = ctx.voice_client
        if vc:
            await vc.disconnect()
            await ctx.send("Disconnected 👋")

async def setup(bot):
    await bot.add_cog(Music(bot))
