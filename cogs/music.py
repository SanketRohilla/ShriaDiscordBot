import discord
from discord import app_commands
from discord.ext import commands
import wavelink

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Start the connection in the background
        bot.loop.create_task(self.setup_nodes())

    async def setup_nodes(self):
        await self.bot.wait_until_ready()
        
        # We use a list of nodes. If one fails, Sky tries the others!
        nodes = [
            # Node 1: High Stability SSL
            wavelink.Node(uri="https://lavalink.oops.wtf:443", password="www.oops.wtf"),
            # Node 2: Backup SSL
            wavelink.Node(uri="https://lava-v4.ajiedev.com:443", password="ajiedev"),
            # Node 3: Third Backup
            wavelink.Node(uri="https://lavalink.lexislohr.com:443", password="youshallnotpass")
        ]
        
        try:
            # Connecting to the pool of nodes
            await wavelink.Pool.connect(nodes=nodes, client=self.bot, cache_capacity=100)
            print("✅ Sky has found a working music node!")
        except Exception as e:
            print(f"❌ All music nodes failed: {e}")

    # =========================
    # 🎵 PLAY COMMAND
    # =========================
    @app_commands.command(name="play", description="Ask Sky to play a song")
    async def play(self, interaction: discord.Interaction, search: str):
        if not interaction.user.voice:
            return await interaction.response.send_message("Get in a VC first. I'm not singing to an empty room. 🙄", ephemeral=True)

        await interaction.response.defer() # Gives Sky time to search

        # Connect or get current player
        vc: wavelink.Player = interaction.guild.voice_client or await interaction.user.voice.channel.connect(cls=wavelink.Player)
        
        # Search for tracks
        tracks = await wavelink.Playable.search(search)
        if not tracks:
            return await interaction.followup.send("I couldn't find that. Your taste is probably just mid. 💀")

        track = tracks[0]
        
        # If already playing, add to queue
        if vc.playing:
            await vc.queue.put(track)
            await interaction.followup.send(f"📝 Added **{track.title}** to the queue. Be patient! 💅")
        else:
            await vc.play(track)
            await interaction.followup.send(f"🎶 Fine, playing: **{track.title}**... don't make me regret this. 😏")

    # =========================
    # ⏭️ SKIP
    # =========================
    @app_commands.command(name="skip", description="Skip this mid song")
    async def skip(self, interaction: discord.Interaction):
        vc: wavelink.Player = interaction.guild.voice_client
        if vc and vc.playing:
            await vc.skip()
            await interaction.response.send_message("Skipped! Finally, something better. 💅")
        else:
            await interaction.response.send_message("Nothing is playing, dummy. 💀", ephemeral=True)

    # =========================
    # 📜 QUEUE
    # =========================
    @app_commands.command(name="queue", description="See what's coming up next")
    async def queue(self, interaction: discord.Interaction):
        vc: wavelink.Player = interaction.guild.voice_client
        if not vc or vc.queue.is_empty:
            return await interaction.response.send_message("The queue is as empty as your brain. 💀", ephemeral=True)

        upcoming = list(vc.queue)[:5] # Show next 5 tracks
        fmt = "\n".join(f"**{i+1}.** {t.title}" for i, t in enumerate(upcoming))
        
        embed = discord.Embed(title="Sky's Upcoming Playlist 💅", description=fmt, color=0xff69b4)
        await interaction.response.send_message(embed=embed)

    # =========================
    # 🛑 STOP
    # =========================
    @app_commands.command(name="stop", description="Stop music and leave")
    async def stop(self, interaction: discord.Interaction):
        vc: wavelink.Player = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
            await interaction.response.send_message("I'm out. 👋")
        else:
            await interaction.response.send_message("I'm not even in a VC? 🙄", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Music(bot))
