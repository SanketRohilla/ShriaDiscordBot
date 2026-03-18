import discord
from discord import app_commands
from discord.ext import commands
import wavelink

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # This starts the music connection in the background
        bot.loop.create_task(self.setup_nodes())

    async def setup_nodes(self):
        await self.bot.wait_until_ready()
        # Using a SECURE node to fix your Railway connection errors
        nodes = [wavelink.Node(uri="https://lavalink.lexislohr.com:443", password="youshallnotpass")]
        await wavelink.Pool.connect(nodes=nodes, client=self.bot)
        print("✅ Sky's Music Node is active!")

    @app_commands.command(name="play", description="Play music with Sky")
    async def play(self, interaction: discord.Interaction, search: str):
        if not interaction.user.voice:
            return await interaction.response.send_message("Get in a VC first. I'm not singing to an empty room. 🙄", ephemeral=True)

        await interaction.response.defer() # Gives the bot time to search
        
        # Connect to voice
        vc: wavelink.Player = interaction.guild.voice_client or await interaction.user.voice.channel.connect(cls=wavelink.Player)
        
        # Search for the song
        tracks = await wavelink.Playable.search(search)
        if not tracks:
            return await interaction.followup.send("I couldn't find that. Your taste is probably just mid. 💀")

        track = tracks[0]
        await vc.play(track)
        await interaction.followup.send(f"🎶 Fine, playing: **{track.title}**... you're welcome. 😏")

    @app_commands.command(name="stop", description="Stop the music and make Sky leave")
    async def stop(self, interaction: discord.Interaction):
        vc: wavelink.Player = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
            await interaction.response.send_message("I'm out. Try not to miss me too much. 👋")
        else:
            await interaction.response.send_message("I'm not even in a VC? 🤨", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Music(bot))
