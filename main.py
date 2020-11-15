import discord
import math
import asyncio
import os
import logging
from datetime import datetime, timedelta
from discord.ext import commands as discord_commands

from settings import Settings
import RockPaperScissors
import commands
import utility
import constants

settings = Settings('settings.json')
bot = discord_commands.Bot(command_prefix=constants.DEFAULT_PREFIX)
bot.remove_command('help')

@bot.command(name='next', help="next <digit> will list the next <digit> events. Max is 9 events. e.g: !next 5")
async def next(ctx, iterations: str="3"):
    next_embed = commands.next(ctx, settings, iterations)
    await ctx.send(embed=next_embed)

@bot.command(name='event', help='Lists current event times')
async def list_events(ctx):
    event_embed = commands.list_events(ctx, settings)
    await ctx.send(embed=event_embed)

@bot.command(name='time', aliases=['daily'], help='Lists the time till daily reset')
async def time(ctx):
    time_embed = commands.time(ctx)
    await ctx.send(embed=time_embed)

@bot.command(name='calculator', aliases=['calc'], help='Cat Game Calculator to help you craft')
async def calculator(ctx):
    await ctx.send(f'Visit https://CatGameCalculator.com to help your crafting needs')

@bot.command(name='rps', help='Rock paper scissors mini game. !rps help for more details!')
async def rps(ctx, selection: str='help'):
    selection = selection.lower()
    embed = None
    if selection == 'help':
        embed = RockPaperScissors.help(settings)
    elif selection == 'rank' or selection == 'ranks':
        embed = RockPaperScissors.rank()
    elif selection == 'profile':
        embed = RockPaperScissors.profile(ctx.message.author)
    else:
        embed = RockPaperScissors.game(ctx.message.author, selection)
    await ctx.send(embed=embed)

@bot.command(name='ping', help='CatGameBot speed test')
async def ping(ctx):
    ms = round(bot.latency, 3)
    await ctx.send(f'Pong! {ms} sec')

@bot.command(name='help', help='Displays this help message')
async def help(ctx):
    help_embed = commands.help(ctx, settings, bot)
    await ctx.send(embed=help_embed)

@bot.command(name='start', help='Starts ping reminders', hidden=True)
async def start(ctx):
    start_response = commands.start(ctx, settings, bot)
    await ctx.send(start_response)

@bot.command(name='stop', help='Stops ping reminders', hidden=True)
async def stop(ctx):
    stop_response = commands.stop(ctx, settings)
    await ctx.send(stop_response)

@bot.command(name='addevent', help='Adds a new mini event. Example: !addevent yyyy-mm-dd yyyy-mm-dd', hidden=True)
async def add_event(ctx, start, stop):
    addevent_response = commands.add_event(ctx, settings, start, stop)
    await ctx.send(addevent_response)

@bot.command(name='delevent', help='Deletes a mini event. optional arg: number. Example: !delevent 3, deletes event nr. 3', hidden=True)
async def delete_event(ctx, *number):
    delevent_response = commands.delete_event(ctx, settings, *number)
    await ctx.send(delevent_response)

@bot.command(name='bonus', help='Lists the full bonus schedule', hidden=True)
async def bonus_list(ctx):
    bonus_response = commands.bonus_list(ctx, settings)
    await ctx.send(embed=bonus_response)

@bot.command(name='delbonus', help='Clears the bonus schedule', hidden=True)
async def bonus_delete(ctx):
    delbonus_response = commands.bonus_delete(ctx, settings)
    await ctx.send(embed=delbonus_response)

@bot.command(name='addbonus', help='Adds a new bonus to the bonus schedule. Example: !addbonus "1min crafting" <@&689721344455213139>', hidden=True)
async def bonus_add(ctx, event_name: str, tag: str):
    add_response = commands.bonus_add(ctx, settings, event_name, tag)
    await ctx.send(embed=add_response)

@bot.command(name="testtag", hidden=True)
async def testtag(ctx):
    await ctx.send("<@&689721344455213139>")

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
                channel = bot.get_channel(settings.channel_reminder)
                await channel.send(f'{minievent.tag} {minievent.event_name} in {utility.format_timedelta(timedelta(seconds=time_difference))}')
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
    logFolder = 'logs'
    logFile = 'CatGameBot.log'
    if not os.path.isdir(logFolder):
        os.makedirs(logFolder)
    
    logging.basicConfig(filename=f'{logFolder}/{logFile}', level=logging.INFO, format='%(asctime)s %(levelname)s:[%(filename)s:%(lineno)d] %(message)s')
        
if __name__ == '__main__':
    setup_logging()
    settings.parse_settings()
    print(f'{settings.prefix=}')
    bot.command_prefix = settings.prefix
    RockPaperScissors.setup_database()
    bot.loop.create_task(do_tasks())
    bot.run(settings.token)