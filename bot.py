import discord
from discord.ext import commands
import aiocron
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID') or 0)
USER_ID = os.getenv('USER_TO_PING') or "@everyone"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

SONG_POSTED_TODAY = False

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} is online.')

@bot.command()
async def servertime(ctx):
    """Check the bot's internal clock to debug scheduling."""
    now = datetime.now().strftime("%I:%M %p")
    await ctx.send(f"🕒 My internal server time is: **{now}**")

@bot.command()
async def check(ctx):
    status = "✅ Posted!" if SONG_POSTED_TODAY else "❌ Not posted yet."
    await ctx.send(f"**Status:** {status}")

@bot.event
async def on_message(message):
    global SONG_POSTED_TODAY
    if message.author.bot: return

    if message.channel.id == CHANNEL_ID:
        # Combined common music platform signatures
        music_platforms = [
            "spotify.com", "spotify.link", "open.spotify", 
            "youtube.com", "youtu.be", "music.apple.com", 
            "soundcloud.com", "tidal.com"
        ]
        
        if any(platform in message.content.lower() for platform in music_platforms):
            SONG_POSTED_TODAY = True
            print(f"🎵 Song detected!")

    await bot.process_commands(message)

# Reset at Midnight
@aiocron.crontab('0 0 * * *')
async def reset_tracker():
    global SONG_POSTED_TODAY
    SONG_POSTED_TODAY = False
    print("🔄 Resetting for the new day.")

# Reminder at 1:00 PM (13:00)
@aiocron.crontab('0 13 * * *')
async def reminder_task():
    global SONG_POSTED_TODAY
    if not SONG_POSTED_TODAY:
        # Using fetch_channel to ensure it works on cloud hosting
        channel = await bot.fetch_channel(CHANNEL_ID)
        if channel:
            await channel.send(f"⚠️ Reminder {USER_ID}: Song of the day is missing!")

if TOKEN:
    bot.run(TOKEN)