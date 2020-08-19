import discord
import asyncio
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
    print('ping reminder is running')
    while settings.run_ping_reminder:
        difference = (datetime.utcnow() - settings.start_time).total_seconds()
        time_difference = constants.SIX_HOURS - (difference % constants.SIX_HOURS)
        if time_difference <= constants.WARNING_TIME:
            if is_event(settings):
                event_iterations = math.floor(difference / constants.ONE_HOUR)
                next_event = (settings.start_event + event_iterations) % 3
                print('ping reminder')
            else:
                asyncio.sleep(constants.WARNING_TIME)
        else:
            print(f'time_difference: {time_difference}')
            sleep_time = time_difference - constants.WARNING_TIME
            await asyncio.sleep(sleep_time)

async def do_tasks():
    await bot.wait_until_ready()
    print(f"Logged in as {bot.user}")
    if settings.start_ping_reminder:
        settings.start_ping_reminder = False
        bot.loop.create_task(ping_reminder())

if __name__ == '__main__':
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