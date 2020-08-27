class EventTime():
    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
    
    def __str__(self):
        return f'{self.start_time} - {self.end_time}'

    def __iter__(self):
        yield from {
            'start_time' : self.start_time.strftime("%B %d %Y, %H:%M:%S"),
            'end_time': self.end_time.strftime("%B %d %Y, %H:%M:%S")
        }.items()