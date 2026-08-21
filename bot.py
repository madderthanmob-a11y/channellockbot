import os
import datetime
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands, tasks

# ---- Config (set these as environment variables on Railway) ----
TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_NAME = os.environ.get("CHANNEL_NAME", "late-night-yap")
TIMEZONE = os.environ.get("TIMEZONE", "America/New_York")

TZ = ZoneInfo(TIMEZONE)
LOCK_TIME = datetime.time(hour=6, minute=0, tzinfo=TZ)      # 6:00 AM
UNLOCK_TIME = datetime.time(hour=22, minute=50, tzinfo=TZ)  # 10:50 PM

intents = discord.Intents.default()
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Tracks whether the channel is currently supposed to be locked.
# Used both to drive message auto-deletion and to recover state after a restart.
channel_locked = False


def compute_current_lock_state() -> bool:
    now = datetime.datetime.now(TZ).time()
    return LOCK_TIME <= now < UNLOCK_TIME


async def set_channel_lock(locked: bool):
    global channel_locked
    channel_locked = locked
    for guild in bot.guilds:
        channel = discord.utils.get(guild.text_channels, name=CHANNEL_NAME)
        if channel is None:
            print(f"Channel '{CHANNEL_NAME}' not found in {guild.name}")
            continue
        overwrite = channel.overwrites_for(guild.default_role)
        overwrite.send_messages = not locked
        await channel.set_permissions(guild.default_role, overwrite=overwrite)
        print(f"{'Locked' if locked else 'Unlocked'} #{CHANNEL_NAME} in {guild.name}")


@tasks.loop(time=LOCK_TIME)
async def lock_channel():
    await set_channel_lock(True)


@tasks.loop(time=UNLOCK_TIME)
async def unlock_channel():
    await set_channel_lock(False)


@bot.event
async def on_message(message: discord.Message):
    # Enforce the lock by deleting messages. This is needed because Discord
    # Administrators bypass the normal "Send Messages" permission overwrite
    # entirely, so permissions alone can't block an admin's role.
    if message.author == bot.user:
        return
    if message.channel.name != CHANNEL_NAME:
        return
    if not channel_locked:
        return
    try:
        await message.delete()
    except (discord.Forbidden, discord.NotFound):
        pass


@bot.event
async def on_ready():
    global channel_locked
    channel_locked = compute_current_lock_state()
    print(f"Logged in as {bot.user} | locking at {LOCK_TIME} / unlocking at {UNLOCK_TIME} ({TIMEZONE})")
    print(f"Startup lock state: {'locked' if channel_locked else 'unlocked'}")
    await set_channel_lock(channel_locked)  # correct permissions in case of drift after downtime

    if not lock_channel.is_running():
        lock_channel.start()
    if not unlock_channel.is_running():
        unlock_channel.start()


bot.run(TOKEN)
