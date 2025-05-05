class Table:
    def __init__(self, table_number):
        self.table_number = table_number
        self.is_reserved = False
        self.reserved_by = None
        self.reservation_time = None

    def reserve(self, customer_name, time):
        if not self.is_reserved:
            self.is_reserved = True
            self.reserved_by = customer_name
            self.reservation_time = time
            return True
        return False

    def unreserve(self):
        if self.is_reserved:
            self.is_reserved = False
            self.reserved_by = None
            self.reservation_time = None

    def __str__(self):
        status = "Reserved" if self.is_reserved else "Available"
        reserved_info = f" by {self.reserved_by} at {self.reservation_time}" if self.is_reserved else ""
        return f"Table {self.table_number}: {status}{reserved_info}"