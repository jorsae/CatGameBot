import discord
import math
import logging
from datetime import datetime, timedelta, timezone
import constants
import utility
from EventTime import EventTime
from Bonus import Bonus

def next(ctx, settings, iterations):
    iterations = utility.clean_iterations(iterations)

    if len(settings.minievents) <= 0:
        embed = discord.Embed(colour=constants.COLOUR_ERROR)
        embed.set_author(name=f'No minievent schedule set.\nPlease let {self.admin} know')
        return embed

    if utility.is_event(settings) is False:
        next_event = utility.get_next_event(settings)
        embed = discord.Embed(colour=constants.COLOUR_ERROR)

        if next_event is None:
            embed.set_author(name='No event is currently running.')
            return embed
        time_left = next_event - datetime.utcnow()

        difference = (datetime.utcnow() - next_event).total_seconds()
        event_iterations = math.floor(difference / constants.SIX_HOURS)
        start_event = (settings.start_event + event_iterations) % len(settings.minievents)
        embed.add_field(name=f'No event is currently running.\nNext event in {time_left}', value=f'Starting event is: {settings.minievents[start_event]}')
        return embed
    
    difference = (datetime.utcnow() - settings.start_time).total_seconds()
    event_iterations = math.floor(difference / constants.SIX_HOURS)
    next_event = (settings.start_event + event_iterations) % len(settings.minievents)

    time_difference = constants.SIX_HOURS - (difference % constants.SIX_HOURS)
    
    event_text = 'event' if iterations <= 1 else f'{iterations} events'
    embed = discord.Embed(colour=constants.COLOUR_OK)
    embed.set_author(name=f'Next {event_text}')
    
    # Event is currently ongoing NOW
    if (constants.SIX_HOURS - time_difference) < 1800:
        time_left = constants.EVENT_DURATION - (constants.SIX_HOURS - time_difference)
        time_left = utility.format_timedelta(timedelta(seconds=time_left))
        embed.add_field(name=f'{settings.minievents[next_event]}', value=f'Time remaining: {time_left}')
        iterations -= 1
    
    for i in range(iterations):
        time_left = i * constants.SIX_HOURS + time_difference
        time_left = utility.format_timedelta(timedelta(seconds=time_left))
        event = (next_event + (i+1)) % len(settings.minievents)
        embed.add_field(name=f'{settings.minievents[event]}', value=f'Time until: {time_left}')

    return embed

def list_events(ctx, settings):
    author = ctx.message.author
    is_admin = utility.is_admin(author, settings)
    
    embed = discord.Embed(colour=constants.COLOUR_OK)
    embed.set_author(name=f'Current events [utc]')

    now = datetime.utcnow()
    index = 0
    for event in settings.event_times:
        name = 'Mini event'
        if is_admin:
            name = f'[{index}] {name}'
            if event.end_time <= now:
                name = f'{name} | Delete'
            embed.add_field(name=name, value=f'{event.start_time} - {event.end_time}', inline=False)
        else:
            if event.end_time > now:
                embed.add_field(name=name, value=f'{event.start_time} - {event.end_time}', inline=False)
        index += 1
    return embed

def time(ctx):
    embed = discord.Embed(colour=constants.COLOUR_OK)
    embed.set_author(name=f'Cat Game time')
    now = datetime.utcnow()
    seconds = ((24 - now.hour - 1) * 60 * 60) + ((60 - now.minute - 1) * 60) + (60 - now.second)
    reset = timedelta(seconds=seconds)
    reset = utility.format_timedelta(reset)

    embed.add_field(name=f'Time till daily reset: {reset}', value=f'[utc] CatGame time: {now}\n', inline=False)
    return embed

def help(ctx, settings, bot):
    author = ctx.message.author
    display_hidden_commands = utility.is_admin(author, settings)

    embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
    embed.set_author(name=f'CatGameBot Help')
    last_command = None
    for command in bot.walk_commands():
        command = bot.get_command(str(command))
        if command is None:
            continue
        if command.hidden is False or display_hidden_commands:
            if last_command != str(command):
                embed.add_field(name=f'{settings.prefix}{command}', value=command.help, inline=False)
            last_command = str(command)
    return embed