import util.config
import util.embeds
import discord
from discord.ext import commands
from mutagen.mp3 import MP3
from random import shuffle
from util.helpers import bar
import asyncio
import time
import os


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vcs = {}
        self.queues = {}
        self.is_playing = {}
        self.volumes = {}
        self.current = {}
        self.start = {}

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id != self.bot.user.id:
            return

        if before.channel is not None and after.channel is None:
            guild = before.channel.guild.id

            self.vcs.pop(guild, None)
            self.queues.pop(guild, None)
            self.is_playing.pop(guild, None)
            self.volumes.pop(guild, None)
            self.current.pop(guild, None)
            self.start.pop(guild, None)

    @discord.slash_command(name="start", description="Join vc and start playing music")
    async def start(self, ctx: discord.ApplicationContext):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.respond(
                embed=util.embeds.error_embed(
                    "You need to be in a voice channel first!"
                ),
                ephemeral=True,
            )

        voice_channel = ctx.author.voice.channel
        if ctx.guild.id in self.vcs:
            voice_client = self.vcs[ctx.guild.id]

            if voice_client.channel == voice_channel:
                return await ctx.respond(
                    embed=util.embeds.error_embed("I'm already in your voice channel!"),
                    ephemeral=True,
                )

            if voice_client.channel != voice_channel:
                await voice_client.move_to(voice_channel)
        else:
            voice_client = await voice_channel.connect()
            self.vcs[ctx.guild.id] = voice_client

        files = [
            os.path.join(util.config.music, f)
            for f in os.listdir(util.config.music)
            if f.endswith(".mp3")
        ]
        if not files:
            return await ctx.respond(
                embed=util.embeds.error_embed(
                    "No MP3 files found in the music folder!"
                ),
                ephemeral=True,
            )

        shuffle(files)

        self.queues[ctx.guild.id] = files
        self.is_playing[ctx.guild.id] = True
        self.volumes.setdefault(ctx.guild.id, 1.0)

        asyncio.create_task(self.play(ctx.guild.id))

        await ctx.respond(
            embed=util.embeds.success_embed(
                f"Joined `{voice_channel.name}` and started playing music!"
            )
        )

    async def play(self, guild):
        voice_client = self.vcs[guild]
        queue = self.queues[guild]

        while True:
            for track in queue:
                if not voice_client.is_connected():
                    return

                volume = self.volumes.get(guild, 1.0)

                self.current[guild] = track
                self.start[guild] = time.time()

                voice_client.play(
                    discord.PCMVolumeTransformer(
                        discord.FFmpegPCMAudio(track), volume=volume
                    )
                )

                while voice_client.is_playing() or voice_client.is_paused():
                    await asyncio.sleep(1)

    @discord.slash_command(
        name="status", description="View current status of SabaRadio"
    )
    async def status(self, ctx: discord.ApplicationContext):
        track = self.current.get(ctx.guild.id)
        start = self.start.get(ctx.guild.id)

        if not track or not start:
            return await ctx.respond(
                embed=util.embeds.error_embed("Nothing currently playing!"),
                ephemeral=True,
            )

        try:
            audio = MP3(track)
            duration = audio.info.length
        except Exception as e:
            return await ctx.respond(e)

        elapsed = time.time() - start
        elapsed = min(elapsed, duration)

        progress = bar(elapsed, duration)
        file = os.path.basename(track)

        await ctx.respond(
            embed=util.embeds.success_embed(f"Now playing: **{file}**").add_field(
                name="Progress",
                value=progress,
            )
        )

    @discord.slash_command(name="queue", description="View current queue of SabaRadio")
    async def queue(self, ctx: discord.ApplicationContext):
        queue = self.queues.get(ctx.guild.id)

        if not queue or len(queue) == 0:
            return await ctx.respond(
                embed=util.embeds.error_embed("The queue is currently empty."),
                ephemeral=True,
            )

        filenames = [os.path.basename(f) for f in queue]

        await ctx.respond(
            embed=util.embeds.success_embed("").add_field(
                name="Current Queue",
                value="\n".join(
                    (
                        f"{i+1}. **{name}**"
                        if name == os.path.basename(self.current.get(ctx.guild.id, ""))
                        else f"{i+1}. {name}"
                    )
                    for i, name in enumerate(filenames)
                ),
            )
        )

    @discord.slash_command(name="volume", description="Change volume of SabaRadio")
    async def volume(self, ctx: discord.ApplicationContext, volume: int):
        if not ctx.voice_client:
            return await ctx.respond(
                embed=util.embeds.error_embed(
                    "You need to be in a voice channel first!"
                ),
                ephemeral=True,
            )

        if not (1 <= volume <= 200):
            return await ctx.respond(
                embed=util.embeds.error_embed("Please enter a value within `1-200`"),
                ephemeral=True,
            )

        if isinstance(ctx.voice_client.source, discord.PCMVolumeTransformer):
            new_volume = volume / 100.0

            ctx.voice_client.source.volume = new_volume
            self.volumes[ctx.guild.id] = new_volume

            await ctx.respond(
                embed=util.embeds.success_embed(f"Volume set to {new_volume * 100.0}%")
            )
        else:
            return await ctx.respond(
                embed=util.embeds.error_embed("No audio playing!"),
                ephemeral=True,
            )

    @discord.slash_command(name="disconnect", description="Disconnect SabaRadio")
    async def disconnect(self, ctx: discord.ApplicationContext):
        if not ctx.voice_client:
            return await ctx.respond(
                embed=util.embeds.error_embed(
                    "You need to be in a voice channel first!"
                ),
                ephemeral=True,
            )

        await ctx.respond(
            embed=util.embeds.success_embed(
                f"Disconnected from `{ctx.author.voice.channel}`!"
            )
        )

        self.vcs.pop(ctx.guild.id, None)
        self.queues.pop(ctx.guild.id, None)
        self.is_playing.pop(ctx.guild.id, None)
        self.volumes.pop(ctx.guild.id, None)
        self.current.pop(ctx.guild.id, None)
        self.start.pop(ctx.guild.id, None)

        await ctx.voice_client.disconnect()


def setup(bot):
    bot.add_cog(Music(bot))
