import discord
from discord.ext import commands
import aiocron
import os
from dotenv import load_dotenv


# 1. Load environment variables
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
# Use a fallback of 0 if ID is missing to prevent the bot from crashing on startup
CHANNEL_ID = int(os.getenv('CHANNEL_ID') or 0)
USER_ID = os.getenv('USER_TO_PING') or "@everyone"

# 2. Setup Intents (Crucial for reading messages)
intents = discord.Intents.default()
intents.message_content = True

# 3. Setup Bot with @everyone permissions
allowed_mentions = discord.AllowedMentions(everyone=True)
bot = commands.Bot(
    command_prefix="!", 
    intents=intents, 
    allowed_mentions=allowed_mentions
)

SONG_POSTED_TODAY = False

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user.name}')
    print(f'📢 Monitoring Channel ID: {CHANNEL_ID}')
    print(f'🔔 Ping Target: {USER_ID}')

@bot.command()
async def check(ctx):
    """Checks if the bot is alive and if the song of the day has been found."""
    if SONG_POSTED_TODAY:
        status_msg = "✅ **Song of the Day has already been posted!**"
    else:
        status_msg = "❌ **No song detected yet.**"
    
    await ctx.send(f"**Bot Status Report:**\n{status_msg}\n{USER_ID}")

@bot.event
async def on_message(message):
    global SONG_POSTED_TODAY
    
    if message.author.bot:
        return

    if message.channel.id == CHANNEL_ID:
        # Broader link detection
        links = ["youtube.com", "youtu.be", "open.spotify.com", "spotify.link", "apple.com/music"]
        
        if any(site in message.content.lower() for site in links):
            SONG_POSTED_TODAY = True
            # This line will now print the user and the link to your Mac Terminal
            print(f"🎵 Song detected from {message.author}: {message.content}")

    await bot.process_commands(message)

# 4. Scheduling Tasks

# Reset at midnight (00:00)
@aiocron.crontab('0 0 * * *')
async def reset_tracker():
    global SONG_POSTED_TODAY
    SONG_POSTED_TODAY = False
    print("🔄 Midnight reset: Waiting for today's song.")

# Reminder at 1:00 PM (13:00)
@aiocron.crontab('0 13 * * *')
async def reminder_task():
    global SONG_POSTED_TODAY
    if not SONG_POSTED_TODAY:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(f"⚠️ Reminder {USER_ID}: No one has posted the Song of the Day yet!")
            print("📣 Reminder sent to Discord.")
        else:
            print("❌ Error: Could not find the channel. Check your CHANNEL_ID.")

# 5. Run the Bot
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ ERROR: No DISCORD_TOKEN found in .env file!")