import discord
import math
import asyncio
import os
import logging
from datetime import datetime, timedelta
from discord.ext import commands
from settings import Settings
import event
import utility
import constants

settings = Settings('settings.json')
bot = commands.Bot(command_prefix=constants.PREFIX)
bot.remove_command('help')

@bot.command(name='next', help="next <digit> will list the next <digit> events. Max is 9 events. e.g: !next 5")
async def next(ctx, iterations: str="1"):
    logging.info(f'next executed by: {ctx.author}, arg: {iterations}')
    event_embed = event.next(ctx, settings, iterations)
    await ctx.send(embed=event_embed)

@bot.command(name='event', help='Lists current event times')
async def list_events(ctx):
    logging.info(f'event executed by: {ctx.author}')
    event_embed = event.list_events(ctx, settings)
    await ctx.send(embed=event_embed)

@bot.command(name='calculator', aliases=['calc'], help='Cat Game Calculator to help you craft')
async def calculator(ctx):
    logging.info(f'calculator executed by: {ctx.author}')
    await ctx.send(f'Visit https://CatGameCalculator.com to help your crafting needs')

@bot.command(name='help', help='Displays this help message')
async def help(ctx):
    logging.info(f'help executed by: {ctx.author}')
    help_embed = event.help(ctx, settings, bot)
    await ctx.send(embed=help_embed)

@bot.command(name='start', help='Starts ping reminders', hidden=True)
async def start(ctx):
    logging.info(f'start executed by: {ctx.author}')
    start_response = event.start(ctx, settings, bot)
    await ctx.send(start_response)

@bot.command(name='stop', help='Stops ping reminders', hidden=True)
async def stop(ctx):
    logging.info(f'stop executed by: {ctx.author}')
    stop_response = event.stop(ctx, settings)
    await ctx.send(stop_response)

@bot.command(name='addevent', help='Adds a new mini event. Example: !addevent yyyy-mm-dd yyyy-mm-dd', hidden=True)
async def add_event(ctx, start, stop):
    logging.info(f'addevent executed by: {ctx.author}')
    addevent_response = event.add_event(ctx, settings, start, stop)
    await ctx.send(addevent_response)

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
        settings.is_running_ping_reminder = True
        difference = (datetime.utcnow() - settings.start_time).total_seconds()
        time_difference = constants.SIX_HOURS - (difference % constants.SIX_HOURS)
        if time_difference <= constants.WARNING_TIME:
            is_event = should_ping(settings)
            if is_event:
                event_iterations = math.floor(difference / constants.SIX_HOURS)
                next_event = (settings.start_event + event_iterations + 1) % 3 # +1 to make it next event and not the current event
                logging.info(f'[{settings.channel_reminder}] Pinging: {constants.EVENTS[next_event]} ({next_event})')
                channel = bot.get_channel(settings.channel_reminder)
                await channel.send(f'{constants.EVENT_PINGS[next_event]} {constants.EVENTS[next_event]} in {utility.format_timedelta(timedelta(seconds=time_difference))}')
            else:
                logging.debug(f'No event is ongoing')
            await asyncio.sleep(constants.WARNING_TIME)
        else:
            sleep_time = time_difference - constants.WARNING_TIME
            logging.info(f'Sleep time: {sleep_time}')
            await asyncio.sleep(sleep_time)
    logging.info('Ping reminder stopped')
    settings.is_running_ping_reminder = False

def should_ping(settings):
    if utility.is_event(settings):
        return True
    next_event = utility.get_next_event(settings)
    if next_event is None:
        return False
    
    return utility.is_event_with_date(settings, next_event)

async def do_tasks():
    await bot.wait_until_ready()
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
    bot.loop.create_task(do_tasks())
    bot.run(settings.token)