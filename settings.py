from datetime import datetime
from event_time import EventTime
import json
import logging

class Settings():
    def __init__(self, settings_file):
        self.settings_file = settings_file
        self.channel_reminder = None
        self.token = None
        self.event_times = []
        
        self.start_time = None
        self.start_event = None
        
        self.start_ping_reminder = True
        self.run_ping_reminder = True
    
    def __str__(self):
        eventTimes = ''
        for event_time in self.event_times:
            eventTimes += f'{event_time} | '
        return f'{self.settings_file}: {self.channel_reminder}. Start: {self.start_time} / {self.start_event}. {eventTimes}'
    
    def parse_settings(self):
        try:
            with open(self.settings_file, 'r') as f:
                data = json.loads(f.read())
            self.token = data.get("token")
            self.channel_reminder = data.get("channel_reminder")
            self.start_time = self.string_to_datetime(data.get("start_time"))
            self.start_event = int(data.get("start_event"))
            
            events = data.get("eventTimes")
            self.event_times.clear()
            for event in events:
                startTime = self.string_to_datetime(event.get("startTime"))
                endTime = self.string_to_datetime(event.get("endTime"))
                self.event_times.append(EventTime(startTime, endTime))
            logging.info('Parsed settings successfully')
            return True
        except Exception as e:
            logging.critical(f'Failed to parse_settings: {e}')
            return False
    
    @staticmethod
    def string_to_datetime(string):
        return datetime.strptime(string, "%B %d %Y, %H:%M:%S")