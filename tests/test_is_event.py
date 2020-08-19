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

def mock_is_event(settings):
    for event in settings.event_times:
        if event.start_time <= now <= event.end_time:
            return True
    return False

def test_is_event():
    assert(mock_is_event(settings)) == True