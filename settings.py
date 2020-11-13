import constants
from datetime import datetime
from MiniEvent import MiniEvent
from EventTime import EventTime
import json
import logging

class Settings():
    def __init__(self, settings_file):
        self.settings_file = settings_file
        self.prefix = constants.DEFAULT_PREFIX
        self.admin = None
        self.minievents = []
        self.channel_reminder = None
        self.token = None
        self.event_times = []
        
        self.start_time = None
        self.start_event = None
        
        self.start_ping_reminder = True
        self.run_ping_reminder = True
        self.is_running_ping_reminder = False
    
    def __str__(self):
        eventTimes = ''
        for event_time in self.event_times:
            eventTimes += f'{event_time} | '
        return f'{self.settings_file}: {self.channel_reminder}. Start: {self.start_time} / {self.start_event}. {eventTimes}'
    
    def parse_settings(self):
        try:
            with open(self.settings_file, 'r') as f:
                data = json.loads(f.read())
            self.prefix = data.get("prefix")
            self.token = data.get("token")
            self.admin = data.get("admin")
            self.channel_reminder = data.get("channel_reminder")
            self.start_time = self.string_to_datetime(data.get("start_time"))
            self.start_event = int(data.get("start_event"))

            minievents = data.get('minievents')
            if minievents is not None:
                for minievent in minievents:
                    event_name = minievent.get("event_name")
                    tag = minievent.get("tag")
                    self.minievents.append(MiniEvent(event_name, tag))
            
            event_times = data.get("event_times")
            self.event_times.clear()
            if event_times is not None:
                for event_time in event_times:
                    startTime = self.string_to_datetime(event_time.get("start_time"))
                    endTime = self.string_to_datetime(event_time.get("end_time"))
                    self.event_times.append(EventTime(startTime, endTime))
            logging.info('Parsed settings successfully')
            return True
        except Exception as e:
            logging.critical(f'Failed to parse_settings: {e}')
            return False
    
    def save_settings(self):
        save_data = {
            'prefix': self.prefix,
            'token': self.token,
            "minievents": [minievent.__dict__ for minievent in self.minievents],
            'channel_reminder': self.channel_reminder,
            'start_event': self.start_event,
            'start_time': self.start_time.strftime("%B %d %Y, %H:%M:%S"),
            'event_times': [dict(eventTime) for eventTime in self.event_times],
            'admin': self.admin
        }

        try:
            json_data = json.dumps(save_data, ensure_ascii=False, indent=4, sort_keys=True, default=str)
            with open(self.settings_file, 'w') as f:
                f.write(json_data)
            return True
        except Exception as e:
            logging.warning(f'Failed to save settings: {e}')
            return False

    def string_to_datetime(self, string):
        return datetime.strptime(string, "%B %d %Y, %H:%M:%S")