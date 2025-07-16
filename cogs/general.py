import util.embeds
import discord
from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="help", description="View SabaRadio's list of commands")
    async def help(self, ctx: discord.ApplicationContext):
        commands = []
        for cmd in self.bot.application_commands:
            if not isinstance(cmd, discord.SlashCommand) or not cmd.id:
                continue

            args = []
            for opt in cmd.options:
                arg_str = f"<{opt.name}: {opt.input_type.name.lower()}>"

                if not opt.required:
                    arg_str = f"[{arg_str}]"

                args.append(arg_str)

            usage = f"</{cmd.name}:{cmd.id}> {' '.join(args)}".strip()
            commands.append(f"* {usage} - {cmd.description or 'No description'}")

        await ctx.respond(
            embed=util.embeds.help_embed("\n".join(commands)), ephemeral=True
        )

    @discord.slash_command(name="about", description="View SabaRadio's about page")
    async def about(self, ctx: discord.ApplicationContext):
        await ctx.respond(embed=util.embeds.about_embed(), ephemeral=True)

    @discord.slash_command(name="stats", description="View SabaRadio's statistics")
    async def stats(self, ctx: discord.ApplicationContext):
        await ctx.respond(
            embed=util.embeds.stats_embed(
                len(self.bot.guilds), round(self.bot.latency * 1000)
            ),
            ephemeral=True,
        )


def setup(bot):
    bot.add_cog(General(bot))
