import math
from datetime import datetime
import constants

def next(ctx, settings, iterations):
    iterations = clean_iterations(iterations)
    print(f'iterations: {iterations}')

    if is_event(settings) is False:
        # TODO: Get the closest event
        return 'No event is currently running'
    
    difference = (datetime.utcnow() - settings.start_time).total_seconds()
    print(f'difference: {difference}')
    event_iterations = math.floor(difference / 3600)
    next_event = (settings.start_event + event_iterations) % 3

    output = ''
    for i in range(iterations):
        event = (next_event + i) % 3
        output += f'Next event: {constants.EVENTS[event]}\n'

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