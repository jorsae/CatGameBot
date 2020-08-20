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
    
    output = f'**Next {iterations} event(s)**\n'
    
    # Event is currently ongoing NOW
    if (constants.SIX_HOURS - time_difference) < 1800:
        time_left = constants.EVENT_DURATION - (constants.SIX_HOURS - time_difference)
        time_left = format_timedelta(timedelta(seconds=time_left))
        output += f'{constants.EVENTS[next_event]} ongoing. Time left: {time_left}\n'
    
    for i in range(iterations):
        time_left = i * constants.SIX_HOURS + time_difference
        time_left = format_timedelta(timedelta(seconds=time_left))
        event = (next_event + (i+1)) % 3
        output += f'{constants.EVENTS[event]} in {time_left}\n'

    return output

def clean_iterations(iterations):
    try:
        iterations = int(iterations)
        if iterations > 10:
            return 10
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