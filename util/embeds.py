import util.config
import discord
from util.emojis import emoji
from util.images import images


def error_embed(message: str):
    return (
        discord.Embed(title="Error", description="An error occurred!", color=0x05B0FF)
        .add_field(
            name="Summary",
            value=f"{message} {emoji('kani_cry')}",
        )
        .set_footer(
            text="SabaRadio",
            icon_url=images["pfp"],
        )
        .set_thumbnail(url=images["pfp"])
    )


def success_embed(title: str, message: str):
    return (
        discord.Embed(
            title=title,
            description=f"{message} {emoji('sabastars')}",
            color=0x05B0FF,
        )
        .set_footer(
            text="SabaRadio",
            icon_url=images["pfp"],
        )
        .set_thumbnail(url=images["pfp"])
    )


def help_embed(commands: str):
    return (
        discord.Embed(
            title="Help",
            description=f"Help for SabaRadio {emoji('sabapray')}",
            color=0x05B0FF,
        )
        .add_field(
            name="Commands",
            value=commands,
        )
        .set_footer(
            text="SabaRadio",
            icon_url=images["pfp"],
        )
        .set_thumbnail(url=images["pfp"])
    )


def about_embed():
    return (
        discord.Embed(
            title="About",
            description=f"About SabaRadio {emoji('Saba_Hug')}",
            color=0x05B0FF,
        )
        .add_field(
            name="Summary",
            value="SabaRadio is a 24/7 music bot for [Sameko Saba's](https://www.youtube.com/@samekosaba) karaoke streams!",
            inline=False,
        )
        .add_field(
            name="Current Karaokes",
            value="\n".join(f"* {k}" for k in util.config.karaokes),
            inline=False,
        )
        .add_field(
            name="More Resources",
            value="For support, please refer to the [GitHub](https://github.com/FireStreaker2/SabaRadio)",
            inline=False,
        )
        .set_footer(
            text="SabaRadio",
            icon_url=images["pfp"],
        )
        .set_thumbnail(url=images["pfp"])
    )


def stats_embed(servers: int, ping: int):
    return (
        discord.Embed(
            title="Statistics",
            description=f"SabaRadio Bot Statistics {emoji('Saba_Blush')}",
            color=0x05B0FF,
        )
        .add_field(
            name="Server Count",
            value=servers,
            inline=False,
        )
        .add_field(
            name="Ping",
            value=f"{ping}ms",
            inline=False,
        )
        .set_footer(
            text="SabaRadio",
            icon_url=images["pfp"],
        )
        .set_thumbnail(url=images["pfp"])
    )
