import math
from datetime import datetime
import constants

def next(ctx, settings):
    if is_event(settings) is False:
        return 'No event running'
    
    difference = (datetime.utcnow() - settings.start_time).total_seconds()
    event_iterations = math.floor(difference / 3600)
    next_event = (settings.start_event + event_iterations) % 3
    return f'Next event: {constants.EVENTS[next_event]}'

    return f'next executed: {settings.settings_file}'

def is_event(settings):
    now = datetime.utcnow()
    for event in settings.event_times:
        if event.start_time <= now <= event.end_time:
            return True
    return False