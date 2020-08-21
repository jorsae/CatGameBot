import main
import discord
import math
from datetime import datetime, timedelta
import constants

def next(ctx, settings, iterations):
    iterations = clean_iterations(iterations)

    if is_event(settings) is False:
        next_event = get_next_event(settings)
        if next_event is None:
            return 'No event is currently running.'
        time_left = next_event - datetime.utcnow()
        return f'No event is currently running.\nNext event in {time_left}'
    
    difference = (datetime.utcnow() - settings.start_time).total_seconds()
    event_iterations = math.floor(difference / constants.SIX_HOURS)
    next_event = (settings.start_event + event_iterations) % 3

    time_difference = constants.SIX_HOURS - (difference % constants.SIX_HOURS)
    
    embed=discord.Embed(colour=discord.Colour.green())
    embed.set_author(name=f'Next {iterations} event(s)')
    
    # Event is currently ongoing NOW
    if (constants.SIX_HOURS - time_difference) < 1800:
        time_left = constants.EVENT_DURATION - (constants.SIX_HOURS - time_difference)
        time_left = format_timedelta(timedelta(seconds=time_left))
        embed.add_field(name=f'{constants.EVENTS[next_event]}', value=f'Time left: {time_left}')
    
    for i in range(iterations):
        time_left = i * constants.SIX_HOURS + time_difference
        time_left = format_timedelta(timedelta(seconds=time_left))
        event = (next_event + (i+1)) % 3
        embed.add_field(name=f'{constants.EVENTS[event]}', value=f'Time left: {time_left}')

    return embed

def list_events(ctx, settings):
    output = "__**Current events [utc]**__\n"
    for event in settings.event_times:
        output += f'{event.start_time} - {event.end_time}\n'
    return output

def stop(ctx, settings):
    author = str(ctx.message.author)
    # Make admin check a utility function
    if author not in settings.admin:
        logging.warning(f'stop was attempted to be executed by: {author}')
        return 'You do not have the permissions for this command'
    
    settings.run_ping_reminder = False
    return 'Ping reminder stopped successfully'

def start(ctx, settings, bot):
    author = str(ctx.message.author)
    # Make admin check a utility function
    if author not in settings.admin:
        logging.warning(f'start was attempted to be executed by: {author}')
        return 'You do not have the permissions for this command'
    
    settings.run_ping_reminder = True
    if settings.is_running_ping_reminder is False:
        bot.loop.create_task(ping_reminder())
        return 'Bot was started successfully | 1'
    
    return 'Bot was started successfully | 2'

def clean_iterations(iterations):
    try:
        iterations = int(iterations)
        if iterations > 9:
            return 9
        if iterations < 1:
            return 1
        return iterations
    except:
        return 1

def is_event(settings):
    now = datetime.utcnow()
    for event in settings.event_times:
        if event.start_time <= now <= event.end_time:
            return True
    return False

def get_next_event(settings):
    now = datetime.utcnow()
    next_event = None
    for event in settings.event_times:
        if event.start_time > now:
            if next_event is None:
                next_event = event.start_time
            else:
                if event.start_time < next_event:
                    next_event = event.start_time
    return next_event

def format_timedelta(tdelta):
    days = tdelta.days
    hours, remainder = divmod(tdelta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    hours = f'0{hours}' if hours < 10 else hours
    minutes = f'0{minutes}' if minutes < 10 else minutes
    seconds = f'0{seconds}' if seconds < 10 else seconds

    if days > 0:
        dayPlural = "days" if days > 1 else "day"
        return f'{days} {dayPlural}, {hours}:{minutes}:{seconds}'
    else:
        return f'{hours}:{minutes}:{seconds}'