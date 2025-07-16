import discord
from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="help", description="View SabaRadio's list of commands")
    async def help(self, ctx: discord.ApplicationContext):
        lines = ["**SabaRadio Commands:**"]

        for cmd in self.bot.application_commands:
            if not isinstance(cmd, discord.SlashCommand):
                continue

            args = []
            for opt in cmd.options:
                arg_str = f"<{opt.name}: {opt.input_type.name.lower()}>"
                if not opt.required:
                    arg_str = f"[{arg_str}]"
                args.append(arg_str)

            usage = f"/{cmd.name} {' '.join(args)}".strip()
            lines.append(f"• `{usage}` — {cmd.description or 'No description'}")

        msg = "\n".join(lines)

        await ctx.respond(msg, ephemeral=True)

    @discord.slash_command(name="about", description="View SabaRadio's about page")
    async def about(self, ctx: discord.ApplicationContext):
        await ctx.respond(
            "SabaRadio is a 24/7 music bot for [Sameko Saba's](https://www.youtube.com/@samekosaba) karaoke streams!\n"
            "Current stored karaokes: \nhttps://www.youtube.com/watch?v=H_Nc-zjRmK4\n\n"
            "For support, please refer to the [GitHub](https://github.com/FireStreaker2/SabaRadio)"
        )

    @discord.slash_command(name="stats", description="View SabaRadio's statistics")
    async def stats(self, ctx: discord.ApplicationContext):
        await ctx.respond(
            f"Servers: {len(self.bot.guilds)}\nPing: {round(self.bot.latency * 1000)}ms"
        )


def setup(bot):
    bot.add_cog(General(bot))
