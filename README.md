<div align="center">
  <div>
    <img src="https://pbs.twimg.com/profile_images/1939105308497854464/luA8qu03_400x400.jpg" height="128" />
    <h1>SabaRadio</h1>
  </div>
  <p>24/7 Saba Karaoke Discord Bot</p>
  <div>
    <img src="https://img.shields.io/badge/Made%20for-Kanikis-blue" />
    <img src="https://img.shields.io/badge/Made%20with-Pycord-blue" />
  </div>
</div>

# About

SabaRadio is a 24/7 music bot for [Sameko Saba's](https://www.youtube.com/@samekosaba) karaoke streams! It utilizes [pycord](https://github.com/Pycord-Development/pycord) to provide Saba's karaoke songs to Discord users 24/7.

# Usage

SabaRadio is currently able to be publicly invited from the [following link](https://sabaradio.firestreaker2.gq/invite), or it can be [selfhosted](https://github.com/FireStreaker2/SabaRadio?tab=readme-ov-file#setup).

## Development

To get started with SabaRadio's Python codebase, simply clone the repository and start working!

### Setup

```bash
$ git clone https://github.com/FireStreaker2/SabaRadio.git
$ cd SabaRadio
$ cp .env.example .env
$ pip install -r requirements.txt
$ python main.py
```

### Project Structure

```
.
├── cogs/ # Cogs for the bot
│   ├── general.py # All general commands
│   ├── __init__.py
│   └── music.py # All music commands
├── main.py # Main bot handler
├── music/ # Music files
├── requirements.txt
└── util
    ├── config.py # Configuration variables
    ├── embeds.py # Prestructured embeds
    ├── emojis.py # Bot Emojis
    ├── helpers.py # Misc. helper functions
    ├── images.py # CDN images used in the bot
    └── __init__.py
```

## Configuration

SabaRadio is very easy to configure in the case of selfhosting, and even less for simple maintence.

### Environment Variables

SabaRadio only uses requires the use of one environment variable, which is the `TOKEN` variable. This can be found from the [Discord Developer Panel](https://discord.com/developers/applications).

### Emojis

SabaRadio improves user experience with cute emojis of Saba! Emoji IDs are located in `util/emojis.py`, but in the case of selfhosting these IDs cannot be used for a different bot. If selfhosting, replace the dictionary with your own emojis uploaded to the "emoji" section of your bot.

# Contributing/Support

If you would like to contribute to SabaRadio, please feel free to open an issue or PR! For support, please also open an issue.

# Credits

- All emojis used in the bot are from [Saba's membership](https://www.youtube.com/@samekosaba/join)!
- Karaokes currently archived by SabaRadio are linked in `util/config.py` or can be viewed via the `/about` command in Discord

# License

[MIT](https://github.com/FireStreaker2/SabaRadio/blob/main/LICENSE)
