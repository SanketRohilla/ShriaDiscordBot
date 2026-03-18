import discord
from discord import app_commands
from discord.ext import commands
import wavelink

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Connect to a public Lavalink node on startup
        bot.loop.create_task(self.setup_nodes())

    async def setup_nodes(self):
        await self.bot.wait_until_ready()
        # Public node: allows Railway to stream music without UDP errors
        nodes = [wavelink.Node(uri="http://lava.link:80", password="youshallnotpass")]
        await wavelink.Pool.connect(nodes=nodes, client=self.bot)
        print("✅ Sky's Music Node is ready!")

    # =========================
    # 🎵 PLAY COMMAND
    # =========================
    @app_commands.command(name="play", description="Ask Sky to play some music")
    async def play(self, interaction: discord.Interaction, search: str):
        if not interaction.user.voice:
            return await interaction.response.send_message("Get in a VC first. I'm not singing to myself. 🙄", ephemeral=True)

        await interaction.response.defer() # Give Sky time to search

        # Connect to voice
        vc: wavelink.Player = interaction.guild.voice_client or await interaction.user.voice.channel.connect(cls=wavelink.Player)
        
        # Search for the song
        tracks = await wavelink.Playable.search(search)
        if not tracks:
            return await interaction.followup.send("I couldn't find that song. Maybe your taste is just too niche? 😭")

        track = tracks[0]
        await vc.play(track)
        await interaction.followup.send(f"🎶 Fine, playing: **{track.title}**... don't make me regret this. 😏")

    # =========================
    # ⏸️ PAUSE/RESUME
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
    @app_commands.command(name="stop", description="Stop the music and leave")
    async def stop(self, interaction: discord.Interaction):
        vc: wavelink.Player = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
            await interaction.response.send_message("I'm out. Try not to miss me too much. 👋")
        else:
            await interaction.response.send_message("I'm not even in a VC? 🙄", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Music(bot))
