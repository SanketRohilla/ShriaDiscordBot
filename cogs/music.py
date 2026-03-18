import discord
from discord import app_commands
from discord.ext import commands
import wavelink

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Start the connection to the music server in the background
        bot.loop.create_task(self.setup_nodes())

    async def setup_nodes(self):
        await self.bot.wait_until_ready()
        
        # Using a stable SSL-secured node to fix the "service not known" error
        nodes = [
            wavelink.Node(
                uri="https://lavalink.lexislohr.com:443", 
                password="youshallnotpass"
            )
        ]
        
        try:
            await wavelink.Pool.connect(nodes=nodes, client=self.bot)
            print("✅ Sky is officially connected to the Music Node!")
        except Exception as e:
            print(f"❌ Music connection failed: {e}")

    # =========================
    # 🎵 PLAY COMMAND
    # =========================
    @app_commands.command(name="play", description="Make Sky play some music for you")
    async def play(self, interaction: discord.Interaction, search: str):
        if not interaction.user.voice:
            return await interaction.response.send_message("Join a VC first. I'm not singing to an empty room. 🙄", ephemeral=True)

        await interaction.response.defer() # Gives Sky time to find the song

        # Connect to the voice channel
        vc: wavelink.Player = interaction.guild.voice_client or await interaction.user.voice.channel.connect(cls=wavelink.Player)
        
        # Search for the track
        tracks = await wavelink.Playable.search(search)
        if not tracks:
            return await interaction.followup.send("I couldn't find that song. Is it even good? 🤨")

        track = tracks[0]
        await vc.play(track)
        await interaction.followup.send(f"🎶 Fine, playing: **{track.title}**... don't say I never do anything for you. 😏")

    # =========================
    # ⏸️ PAUSE / RESUME
    # =========================
    @app_commands.command(name="pause", description="Pause the music")
    async def pause(self, interaction: discord.Interaction):
        vc: wavelink.Player = interaction.guild.voice_client
        if vc and not vc.paused:
            await vc.pause(True)
            await interaction.response.send_message("Paused. Finally, some peace and quiet. 😌")
        else:
            await interaction.response.send_message("It's already paused, dummy. 💀", ephemeral=True)

    @app_commands.command(name="resume", description="Resume the music")
    async def resume(self, interaction: discord.Interaction):
        vc: wavelink.Player = interaction.guild.voice_client
        if vc and vc.paused:
            await vc.pause(False)
            await interaction.response.send_message("Ugh, fine. Back to the music. 🙄")
        else:
            await interaction.response.send_message("Nothing is even paused? 🤨", ephemeral=True)

    # =========================
    # ⏭️ SKIP
    # =========================
    @app_commands.command(name="skip", description="Skip this song")
    async def skip(self, interaction: discord.Interaction):
        vc: wavelink.Player = interaction.guild.voice_client
        if vc:
            await vc.skip()
            await interaction.response.send_message("Skipped! That song was mid anyway. 💅")
        else:
            await interaction.response.send_message("There's nothing to skip. 💀", ephemeral=True)

    # =========================
    # 🛑 STOP
    # =========================
    @app_commands.command(name="stop", description="Stop the music and make Sky leave")
    async def stop(self, interaction: discord.Interaction):
        vc: wavelink.Player = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
            await interaction.response.send_message("I'm out. Try not to miss me too much. 👋")
        else:
            await interaction.response.send_message("I'm not even in a VC? 🙄", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Music(bot))
