import discord
from discord.ext import commands
import wavelink

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            node = wavelink.Node(
                uri="https://lavalink-2026-production-536b.up.railway.app",
                password="mysuperpass"
            )

            await wavelink.Pool.connect(client=self.bot, nodes=[node])
            print("✅ Lavalink connected!")
        except Exception as e:
            print(f"❌ Lavalink error: {e}")

    # 🎵 PLAY
    @commands.command(name="pl")
    async def play(self, ctx, *, search: str):
        if not ctx.author.voice:
            return await ctx.send("Join VC first 😭")

        player: wavelink.Player = ctx.voice_client

        if not player:
            player = await ctx.author.voice.channel.connect(cls=wavelink.Player)

        tracks = await wavelink.Playable.search(search)

        if not tracks:
            return await ctx.send("No results 😭")

        track = tracks[0]

        await player.play(track)

        await ctx.send(f"🎵 Now playing: **{track.title}**")

    # ⏸ PAUSE
    @commands.command(name="ps")
    async def pause(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.pause()
            await ctx.send("Paused ⏸")

    # ▶ RESUME
    @commands.command(name="rs")
    async def resume(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.resume()
            await ctx.send("Resumed ▶")

    # ⏹ STOP
    @commands.command(name="st")
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.stop()
            await ctx.send("Stopped ⏹")

    # ❌ DISCONNECT
    @commands.command(name="dc")
    async def dc(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("Disconnected 👋")

async def setup(bot):
    await bot.add_cog(Music(bot))
