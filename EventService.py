import EventReservation

class EventService:
    def __init__(self, event_reservations=None):
        self.event_reservations = event_reservations if event_reservations else []

    def make_event_reservation(self):
        print("\n--- Event Reservation ---")
        name = input("Customer Name: ")
        event_type = input("Event Type (e.g., birthday, corporate): ")
        date = input("Date (YYYY-MM-DD): ")
        time = input("Time (e.g., 7 PM): ")
        num_guests = input("Number of Guests: ")

        
        if any(existing.date == date and existing.time == time for existing in self.event_reservations):
                print("⚠️ Sorry, there's already an event booked at that date and time.")
                return
        else:
            reservation = EventReservation.EventReservation(name, event_type, date, time, num_guests)
            self.event_reservations.append(reservation)
            print("\n✅ Event reservation successful!")
            print(self.generate_confirmation_message(reservation))

    def generate_confirmation_message(self, reservation):
        return (
            "\n📩 Confirmation:\n"
            f"Dear {reservation.customer_name}, your {reservation.event_type.title()} event has been booked!\n"
            f"📅 Date: {reservation.date}\n"
            f"⏰ Time: {reservation.time}\n"
            f"👥 Guests: {reservation.num_guests}\n"
            f"📍 Venue: MIU Diner\n" 
            "Thank you for choosing us!\n"
        )

    def show_event_reservations(self):
        print("\n--- Upcoming Event Reservations ---")
        if not self.event_reservations:
            print("No events booked.")
        else:
            for res in self.event_reservations:
                print(f"- {res}")