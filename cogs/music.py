import util.config
import util.embeds
import util.helpers
import discord
from discord.ext import commands
from mutagen.mp3 import MP3
from random import shuffle
from time import time
import asyncio
import os


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tasks = {}
        self.vcs = {}
        self.queues = {}
        self.is_playing = {}
        self.volumes = {}
        self.current = {}
        self.start = {}
        self.pauses = {}
        self.elapsed = {}

        self.admin_only = {}

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        if member.id == self.bot.user.id:
            if (
                before.channel is not None
                and after.channel is None
                and not member.guild.voice_client
            ):
                self.reset(before.channel.guild.id)
            return

        for guild, voice_client in self.vcs.items():
            if not voice_client or not voice_client.is_connected():
                self.reset(guild)
                continue

            vc = voice_client.channel
            if before.channel == vc or after.channel == vc:
                if (
                    len([m for m in vc.members if not m.bot]) == 0
                    and voice_client.is_playing()
                ):
                    voice_client.pause()

                    now = time()
                    self.pauses[vc.guild.id] = now
                    self.elapsed[vc.guild.id] += now - self.start[vc.guild.id]

                elif voice_client.is_paused():
                    voice_client.resume()

                    self.start[vc.guild.id] = time()
                    self.pauses[vc.guild.id] = None

    @discord.slash_command(name="start", description="Join vc and start playing music")
    async def start(self, ctx: discord.ApplicationContext):
        if self.admin_only.get(ctx.guild.id, False):
            if not ctx.author.guild_permissions.administrator:
                return await ctx.respond(
                    embed=util.embeds.error_embed("Only admins can use this command."),
                    ephemeral=True,
                )

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.respond(
                embed=util.embeds.error_embed(
                    "You need to be in a voice channel first!"
                ),
                ephemeral=True,
            )

        voice_channel = ctx.author.voice.channel
        voice_client = ctx.guild.voice_client
        if voice_client:
            if voice_client.channel != voice_channel:
                await voice_client.move_to(voice_channel)
            else:
                return await ctx.respond(
                    embed=util.embeds.error_embed("I'm already in your voice channel!"),
                    ephemeral=True,
                )
        else:
            voice_client = await voice_channel.connect()

        self.vcs[ctx.guild.id] = voice_client

        await ctx.guild.change_voice_state(
            channel=voice_channel, self_mute=False, self_deaf=True
        )

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

        existing = self.tasks.get(ctx.guild.id)
        if existing and not existing.done():
            existing.cancel()

        task = asyncio.create_task(self.play(ctx.guild.id))
        self.tasks[ctx.guild.id] = task

        await ctx.respond(
            embed=util.embeds.success_embed(
                "Success", f"Joined <#{voice_channel.id}> and started playing music!"
            )
        )

    async def play(self, guild: int):
        voice_client = self.vcs[guild]
        queue = self.queues[guild]

        while True:
            for track in queue:
                if not voice_client.is_connected():
                    return

                volume = self.volumes.get(guild, 1.0)

                self.current[guild] = track
                self.elapsed[guild] = 0.0
                self.pauses[guild] = None
                self.start[guild] = time()

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

        progress = util.helpers.bar(
            (
                self.elapsed[ctx.guild.id]
                if self.pauses[ctx.guild.id]
                else (time() - self.start[ctx.guild.id]) + self.elapsed[ctx.guild.id]
            ),
            duration,
        )
        file = os.path.basename(track)

        await ctx.respond(
            embed=util.embeds.success_embed(
                "Status", f"Now playing: **{file}**"
            ).add_field(
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
            embed=util.embeds.success_embed("Queue", "").add_field(
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
    async def volume(
        self,
        ctx: discord.ApplicationContext,
        volume: discord.Option(int, "Percentage volume of SabaRadio from 1-200%"),  # type: ignore
    ):
        if self.admin_only.get(ctx.guild.id, False):
            if not ctx.author.guild_permissions.administrator:
                return await ctx.respond(
                    embed=util.embeds.error_embed("Only admins can use this command."),
                    ephemeral=True,
                )

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
                embed=util.embeds.success_embed(
                    "Success", f"Volume set to {new_volume * 100.0}%"
                )
            )
        else:
            return await ctx.respond(
                embed=util.embeds.error_embed("No audio playing!"),
                ephemeral=True,
            )

    @discord.slash_command(name="disconnect", description="Disconnect SabaRadio")
    async def disconnect(self, ctx: discord.ApplicationContext):
        if self.admin_only.get(ctx.guild.id, False):
            if not ctx.author.guild_permissions.administrator:
                return await ctx.respond(
                    embed=util.embeds.error_embed("Only admins can use this command."),
                    ephemeral=True,
                )

        if not ctx.voice_client:
            return await ctx.respond(
                embed=util.embeds.error_embed("Not currently connected!"),
                ephemeral=True,
            )

        if (
            not ctx.author.voice
            or not ctx.author.voice.channel
            or ctx.author.voice.channel != ctx.voice_client.channel
        ):
            return await ctx.respond(
                embed=util.embeds.error_embed("You must be in the same vc!"),
                ephemeral=True,
            )

        self.reset(ctx.guild.id)
        await ctx.respond(
            embed=util.embeds.success_embed(
                "Success", f"Disconnected from <#{ctx.voice_client.channel.id}>!"
            )
        )
        await ctx.voice_client.disconnect()

    def reset(self, guild: int):
        self.vcs.pop(guild, None)
        self.queues.pop(guild, None)
        self.is_playing.pop(guild, None)
        self.volumes.pop(guild, None)
        self.current.pop(guild, None)
        self.start.pop(guild, None)
        self.pauses.pop(guild, None)
        self.elapsed.pop(guild, None)

        task = self.tasks.pop(guild, None)
        if task and not task.done():
            task.cancel()

    @discord.slash_command(
        name="toggleadmin",
        description="Only allow administrators to initialize SabaRadio",
    )
    @commands.has_permissions(administrator=True)
    async def toggleadmin(self, ctx: discord.ApplicationContext):
        current = self.admin_only.get(ctx.guild.id, False)
        self.admin_only[ctx.guild.id] = not current

        await ctx.respond(
            embed=util.embeds.success_embed(
                "Success",
                f"Admin-only mode has been **{'enabled' if not current else 'disabled'}** for select commands",
            ),
            ephemeral=True,
        )


def setup(bot: commands.Bot):
    bot.add_cog(Music(bot))
