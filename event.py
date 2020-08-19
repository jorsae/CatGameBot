from datetime import datetime
import constants

def next(ctx, settings):
    if is_event(settings) is False:
        return 'No event running'
    
    difference = settings.start
    return f'next executed: {settings.settings_file}'

def is_event(settings):
    now = datetime.utcnow()
    for event in settings.event_times:
        if event.start_time <= now <= event.end_time:
            return True
    return False