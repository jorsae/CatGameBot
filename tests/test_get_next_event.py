import pytest
import sys
sys.path.append('.')
from settings import Settings
from datetime import datetime

now = datetime(2020, 8, 15, 23, 19) # 15.08.2020 11:19 pm
settings = None

@pytest.fixture(scope="module", autouse=True)
def create_settings():
    global settings
    settings = Settings('tests/test_settings.json')
    settings.parse_settings()

def mock_get_next_event(settings):
    next_event = None
    for event in settings.event_times:
        if event.start_time > now:
            if next_event is None:
                next_event = event.start_time
            else:
                if event.start_time < next_event:
                    next_event = event.start_time
    return next_event

def test_get_next_event():
    assert(mock_get_next_event(settings)) == datetime(2020, 8, 19, 0, 0)
