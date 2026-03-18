import discord
from discord import app_commands
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
                client=self.bot,
                cache_capacity=100
            )
            print("✅ Sky has found a working music node!")
        except Exception as e:
            print(f"❌ Lavalink connection failed: {e}")

    # =========================
    # 🎵 PLAY
    # =========================
    @app_commands.command(name="play", description="Play a song")
    async def play(self, interaction: discord.Interaction, search: str):
        if not interaction.user.voice:
            return await interaction.response.send_message(
                "Join a VC first. 🙄", ephemeral=True
            )

        await interaction.response.defer()

        vc: wavelink.Player = (
            interaction.guild.voice_client or
            await interaction.user.voice.channel.connect(cls=wavelink.Player)
        )

        tracks = await wavelink.Playable.search(search)

        if not tracks:
            return await interaction.followup.send("No results found 💀")

        track = tracks[0]

        if vc.playing:
            await vc.queue.put(track)
            await interaction.followup.send(f"📝 Added **{track.title}** to queue")
        else:
            await vc.play(track)
            await interaction.followup.send(f"🎶 Playing **{track.title}**")

    # =========================
    # ⏭️ SKIP
    # =========================
    @app_commands.command(name="skip", description="Skip current song")
    async def skip(self, interaction: discord.Interaction):
        vc: wavelink.Player = interaction.guild.voice_client

        if vc and vc.playing:
            await vc.skip()
            await interaction.response.send_message("⏭️ Skipped")
        else:
            await interaction.response.send_message("Nothing playing ❌", ephemeral=True)

    # =========================
    # 📜 QUEUE
    # =========================
    @app_commands.command(name="queue", description="Show queue")
    async def queue(self, interaction: discord.Interaction):
        vc: wavelink.Player = interaction.guild.voice_client

        if not vc or vc.queue.is_empty:
            return await interaction.response.send_message("Queue empty 💀", ephemeral=True)

        upcoming = list(vc.queue)[:5]

        desc = "\n".join(f"**{i+1}.** {t.title}" for i, t in enumerate(upcoming))

        embed = discord.Embed(
            title="🎶 Upcoming Songs",
            description=desc,
            color=0xff69b4
        )

        await interaction.response.send_message(embed=embed)

    # =========================
    # ⏸️ PAUSE
    # =========================
    @app_commands.command(name="pause", description="Pause song")
    async def pause(self, interaction: discord.Interaction):
        vc: wavelink.Player = interaction.guild.voice_client

        if vc and vc.playing:
            await vc.pause(True)
            await interaction.response.send_message("⏸️ Paused")
        else:
            await interaction.response.send_message("Nothing playing ❌", ephemeral=True)

    # =========================
    # ▶️ RESUME
    # =========================
    @app_commands.command(name="resume", description="Resume song")
    async def resume(self, interaction: discord.Interaction):
        vc: wavelink.Player = interaction.guild.voice_client

        if vc and vc.paused:
            await vc.pause(False)
            await interaction.response.send_message("▶️ Resumed")
        else:
            await interaction.response.send_message("Nothing paused ❌", ephemeral=True)

    # =========================
    # 🔊 VOLUME
    # =========================
    @app_commands.command(name="volume", description="Set volume (0-100)")
    async def volume(self, interaction: discord.Interaction, vol: int):
        vc: wavelink.Player = interaction.guild.voice_client

        if not vc:
            return await interaction.response.send_message("Not in VC ❌", ephemeral=True)

        vol = max(0, min(vol, 100))
        await vc.set_volume(vol)

        await interaction.response.send_message(f"🔊 Volume set to {vol}%")

    # =========================
    # 🛑 STOP
    # =========================
    @app_commands.command(name="stop", description="Stop and leave")
    async def stop(self, interaction: discord.Interaction):
        vc: wavelink.Player = interaction.guild.voice_client

        if vc:
            await vc.disconnect()
            await interaction.response.send_message("👋 Left VC")
        else:
            await interaction.response.send_message("Not in VC ❌", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Music(bot))
