from datetime import datetime

# Clean iterations (argument from !next) to make sure it's safe
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

# returns true if the user is an admin. False otherwise
def is_admin(author, settings):
    if type(author) == str:
        return author in settings.admin
    else:
        return str(author) in settings.admin

# returns true/false if an event is currently running
def is_event(settings):
    now = datetime.utcnow()
    for event in settings.event_times:
        if event.start_time <= now <= event.end_time:
            return True
    return False

# returns true/false if an event is currently running during the set date
def is_event_with_date(settings, date):
    for event in settings.event_times:
        if event.start_time <= date <= event.end_time:
            return True
    return False

# Returns the start_time of the next event coming up
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

# Formats a timedelta into readable text
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

# Cleans up bonus schedule. i.e: if a bonus in the middle is deleted.
def number_is_clean(numbers, event_list):
    events = len(event_list) - 1
    for i in numbers:
        if i > events or i < 0:
            return False
    return True

# Convers list of digits with type str to type int
def clean_number_input(number):
    numbers = []
    for i in enumerate(number):
        try:
            numbers.append(int(i[1]))
        except:
            return None
    return numbers

# Get a commands aliases
def get_aliases(aliases):
    if aliases == []:
        return ''
    else:
        output = ' | ('
        for alias in aliases:
            output += f'{alias}, '
        output = output[:-2]
        return f'{output})'