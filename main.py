import discord
import asyncio
import os
import logging
from datetime import datetime
from discord.ext import commands
from settings import Settings
import event
import constants

settings = Settings('settings.json')
bot = commands.Bot(command_prefix='!')

@bot.command(name='list')
async def test(ctx, arg):
    await ctx.send(arg)

@bot.command(name='next')
async def next(ctx, iterations: str="1"):
    logging.info(f'next executed by: {ctx.author}, arg: {iterations}')
    await ctx.send(event.next(ctx, settings, iterations))

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
    await bot.process_commands(message)

async def ping_reminder():
    logging.info(f'Ping reminder is running: {settings.run_ping_reminder}')
    while settings.run_ping_reminder:
        difference = (datetime.utcnow() - settings.start_time).total_seconds()
        time_difference = constants.SIX_HOURS - (difference % constants.SIX_HOURS)
        if time_difference <= constants.WARNING_TIME:
            if event.is_event(settings):
                event_iterations = math.floor(difference / constants.ONE_HOUR)
                next_event = (settings.start_event + event_iterations) % 3
                logging.info(f'Ping reminder: {constants.EVENTS[event]} | {event_iterations}, {next_event}')
            else:
                logging.debug(f'No event is ongoing')
                asyncio.sleep(constants.WARNING_TIME)
        else:
            sleep_time = time_difference - constants.WARNING_TIME
            logging.info(f'Sleep time: {sleep_time}')
            await asyncio.sleep(sleep_time)

async def do_tasks():
    await bot.wait_until_ready()
    print(f'Logged in as {bot.user}')
    logging.info(f'Logged in as {bot.user}')
    if settings.start_ping_reminder:
        settings.start_ping_reminder = False
        bot.loop.create_task(ping_reminder())

def setup_logging():
    logFolder = 'logs'
    logFile = 'CatGameBot.log'
    if not os.path.isdir(logFolder):
        os.makedirs(logFolder)
    
    logging.basicConfig(filename=f'{logFolder}/{logFile}', level=logging.INFO, format='%(asctime)s %(levelname)s:[%(filename)s:%(lineno)d] %(message)s')
        
if __name__ == '__main__':
    setup_logging()
    settings.parse_settings()
    # print(settings)
    # print(event.get_next_event(settings))
    # print(event.is_event(settings))
    # print(event.next(None, settings, 1))
    # print(event.next(None, settings, 3))
    # print(event.next(None, settings, 13))
    # print(event.next(None, settings, "asd"))
    bot.loop.create_task(do_tasks())
    bot.run(settings.token)