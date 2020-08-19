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
    event_iterations = math.floor(difference / constants.ONE_HOUR)
    next_event = (settings.start_event + event_iterations) % 3

    time_difference = constants.SIX_HOURS - (difference % constants.SIX_HOURS)
    
    output = f'Next {iterations} event(s)\n'

    # Event is currently ongoing NOW
    if (constants.SIX_HOURS - time_difference) < 1800:
        b = constants.SIX_HOURS - time_difference
        event = (next_event - 1) % 3
        a = timedelta(seconds=b)
        output += f'{constants.EVENTS[event]} ongoing. Time left: {a}\n'
    
    for i in range(iterations):
        time_left = i*constants.SIX_HOURS + time_difference
        a = timedelta(seconds=time_left)
        event = (next_event + i) % 3
        output += f'[{i+1}]: {constants.EVENTS[event]} in {a}\n'

    return output

def clean_iterations(iterations):
    if type(iterations) is not int:
        return 1
    else:
        if iterations > 10:
            return 10
        elif iterations < 0:
            return 1
        return iterations

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