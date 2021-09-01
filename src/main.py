import discord
import math
import asyncio
import os
import logging
from datetime import datetime, timedelta
from discord.ext import commands as discord_commands

from settings import Settings
from cogs import *
import RockPaperScissors
import utility
import constants

settings = Settings('../settings.json')
bot = discord_commands.Bot(command_prefix=constants.DEFAULT_PREFIX)
bot.remove_command('help')

@bot.event
async def on_message(message: discord.Message):
    await bot.wait_until_ready()
    message.content = (
        message.content
        .replace("—", "--")
        .replace("'", "′")
        .replace("‘", "′")
        .replace("’", "′")
    )
    if message.content.startswith(settings.prefix):
        logging.info(f'[{str(message.author)}] Command: "{message.content}"')

    await bot.process_commands(message)

async def ping_reminder():
    logging.info(f'Ping reminder is running: {settings.run_ping_reminder}')
    while settings.run_ping_reminder:
        settings.is_running_ping_reminder = True
        difference = (datetime.utcnow() - settings.start_time).total_seconds()
        time_difference = constants.SIX_HOURS - (difference % constants.SIX_HOURS)

        if len(settings.minievents) <= 0:
            logging.critical('No minievent schedule is set. Sleeping 5min, then checking again')
            await asyncio.sleep(constants.WARNING_TIME)
            continue

        if time_difference <= constants.WARNING_TIME:
            is_event = should_ping(settings)
            if is_event:
                event_iterations = math.floor(difference / constants.SIX_HOURS)
                next_minievent = (settings.start_event + event_iterations + 1) % len(settings.minievents) # +1 to make it next event and not the current event
                minievent = settings.minievents[next_minievent]
                logging.info(f'[{settings.channel_reminder}] Pinging: {minievent.event_name} ({minievent.tag})')
                try:
                    channel = bot.get_channel(settings.channel_reminder)
                    msg = await channel.send(f'{minievent.tag} {minievent.event_name} in {utility.format_timedelta(timedelta(seconds=time_difference))}')
                    await msg.publish()
                except Exception as e:
                    logging.critical(f'Failed to publish for event')
            else:
                logging.info(f'No event is ongoing')
            await asyncio.sleep(constants.WARNING_TIME)
        else:
            sleep_time = time_difference - constants.WARNING_TIME
            logging.info(f'Sleep time: {sleep_time}')
            await asyncio.sleep(sleep_time)
    logging.info('Ping reminder stopped')
    settings.is_running_ping_reminder = False

def should_ping(settings):
    if utility.is_event_with_date(settings, datetime.utcnow() + timedelta(seconds=constants.WARNING_TIME)):
        return True
    return False

async def do_tasks():
    await bot.wait_until_ready()
    logging.info(f'Logged in as {bot.user}')
    if settings.start_ping_reminder:
        settings.start_ping_reminder = False
        bot.loop.create_task(ping_reminder())

def setup_logging():
    logFolder = '../logs'
    logFile = 'CatGameBot.log'
    if not os.path.isdir(logFolder):
        os.makedirs(logFolder)
    
    logging.basicConfig(filename=f'{logFolder}/{logFile}', level=logging.INFO, format='%(asctime)s %(levelname)s:[%(filename)s:%(lineno)d] %(message)s')
        
if __name__ == '__main__':
    setup_logging()
    settings.parse_settings()
    bot.command_prefix = settings.prefix
    RockPaperScissors.setup_database()
    
    bot.add_cog(General(bot, settings))
    bot.add_cog(Moderator(bot, settings))
    bot.add_cog(Admin(bot, settings))

    bot.loop.create_task(do_tasks())
    bot.run(settings.token)