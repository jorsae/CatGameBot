class Bonus():
    def __init__(self, event_name, tag):
        self.event_name = event_name
        self.tag = tag
    
    def __str__(self):
        return f'{self.event_name}'