class EventReservation:
    def __init__(self, customer_name, event_type, date, time, num_guests):
        self.customer_name = customer_name
        self.event_type = event_type
        self.date = date
        self.time = time
        self.num_guests = num_guests

    def __str__(self):
        return f"{self.event_type} on {self.date} at {self.time} for {self.num_guests} guests."