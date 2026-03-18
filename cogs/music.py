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
        
        # We use a Pool of nodes so if one fails, Sky tries the next!
        nodes = [
            # Node 1: High Stability (SSL)
            wavelink.Node(uri="https://lavalink.oops.wtf:443", password="www.oops.wtf"),
            # Node 2: Backup (Non-SSL)
            wavelink.Node(uri="http://new-york-node-1.vortexcloud.xyz:5021", password="discord.gg/W2GheK3F9m"),
            # Node 3: Secondary Backup
            wavelink.Node(uri="https://lava-v4.ajiedev.com:443", password="ajiedev")
        ]
        
        try:
            await wavelink.Pool.connect(nodes=nodes, client=self.bot, cache_capacity=100)
            print("✅ Sky found a working music server!")
        except Exception as e:
            print(f"❌ All music nodes failed: {e}")

    # =========================
    # 🎵 PLAY COMMAND
    # =========================
    @app_commands.command(name="play", description="Make Sky play a song")
    async def play(self, interaction: discord.Interaction, search: str):
        if not interaction.user.voice:
            return await interaction.response.send_message("Get in a VC first. I'm not singing to an empty room. 🙄", ephemeral=True)

        await interaction.response.defer()
        vc: wavelink.Player = interaction.guild.voice_client or await interaction.user.voice.channel.connect(cls=wavelink.Player)
        
        # Search for the track
        tracks = await wavelink.Playable.search(search)
        if not tracks:
            return await interaction.followup.send("I couldn't find that song. Your taste is probably just mid. 💀")

        track = tracks[0]
        await vc.queue.put(track)
        
        if not vc.playing:
            await vc.play(vc.queue.get())
            await interaction.followup.send(f"🎶 Fine, playing: **{track.title}**... don't make me regret this. 😏")
        else:
            await interaction.followup.send(f"📝 Added **{track.title}** to the queue. Be patient, okay? 🙄")

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
            await interaction.response.send_message("There's nothing playing, dummy. 💀", ephemeral=True)

    # =========================
    # 📜 QUEUE
    # =========================
    @app_commands.command(name="queue", description="See what's coming up next")
    async def queue(self, interaction: discord.Interaction):
        vc: wavelink.Player = interaction.guild.voice_client
        if not vc or vc.queue.is_empty:
            return await interaction.response.send_message("The queue is as empty as your brain. 💀", ephemeral=True)

        upcoming = list(vc.queue)[:5] # Show next 5 songs
        fmt = "\n".join(f"**{i+1}.** {t.title}" for i, t in enumerate(upcoming))
        
        embed = discord.Embed(title="Sky's Upcoming Playlist 💅", description=fmt, color=0x3498db)
        await interaction.response.send_message(embed=embed)

    # =========================
    # ⏸️ PAUSE / RESUME
    # =========================
    @app_commands.command(name="pause", description="Shut the music up for a sec")
    async def pause(self, interaction: discord.Interaction):
        vc: wavelink.Player = interaction.guild.voice_client
        if vc and not vc.paused:
            await vc.pause(True)
            await interaction.response.send_message("Paused. Finally, some peace and quiet. 😌")

    @app_commands.command(name="resume", description="Back to the music")
    async def resume(self, interaction: discord.Interaction):
        vc: wavelink.Player = interaction.guild.voice_client
        if vc and vc.paused:
            await vc.pause(False)
            await interaction.response.send_message("Ugh, fine. Let's keep going. 🙄")

    # =========================
    # 🛑 STOP
    # =========================
    @app_commands.command(name="stop", description="Stop music and leave")
    async def stop(self, interaction: discord.Interaction):
        vc: wavelink.Player = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
            await interaction.response.send_message("I'm out. Try not to miss me too much. 👋")

async def setup(bot):
    await bot.add_cog(Music(bot))
