import pytest
import sys
sys.path.append('.')
from settings import Settings
from datetime import datetime

settings = Settings('test_settings.json')

#TODO: This does not read from the settings file

@pytest.fixture(scope="module")
def create_settings():
    settings.parse_settings()

def mock_is_event(settings):
    now = datetime(2020, 8, 15, 23, 19) # 15.08.2020 11:19 pm
    for event in settings.event_times:
        if event.start_time <= now <= event.end_time:
            return True
    return False

def mock_get_next_event(settings):
    now = datetime(2020, 8, 15, 23, 19, 5, 597670) # 15.08.2020 11:19 pm
    next_event = None
    for event in settings.event_times:
        if event.start_time > now:
            if next_event is None:
                next_event = event.start_time
            else:
                if event.start_time < next_event:
                    next_event = event.start_time
    return next_event

def test_is_event():
    assert(mock_is_event(settings)) == False


def test_get_next_event():
    assert(mock_get_next_event(settings)) == None
