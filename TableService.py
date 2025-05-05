import Table

class TableService:
    def __init__(self, tables=None):
        self.tables = tables if tables else [Table.Table(i) for i in range(1, 6)]

    def select_table(self):
        print("\nSelect a table:")
        available_tables = [table for table in self.tables if not table.is_reserved]
        if not available_tables:
            print("No tables currently available.")
            return None
        for table in available_tables:
            print(f"- Table {table.table_number}")
        while True:
            try:
                table_number = int(input("Enter table number: "))
                selected_table = next((table for table in available_tables if table.table_number == table_number), None)
                if selected_table:
                    return selected_table
                else:
                    print("Invalid table number. Please choose from the available tables.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def reserve_table(self):
        print("\n--- Table Reservation ---")
        customer_name = input("Customer Name: ")
        print("\nAvailable Tables:")
        available_tables = [table for table in self.tables if not table.is_reserved]
        if not available_tables:
            print("No tables currently available for reservation.")
            return
        for table in available_tables:
            print(f"- Table {table.table_number}")
        while True:
            try:
                table_number_to_reserve = int(input("Enter the table number you want to reserve: "))
                table_to_reserve = next((table for table in available_tables if table.table_number == table_number_to_reserve), None)
                if table_to_reserve:
                    reservation_time = input("Enter reservation time (e.g., 7:30 PM): ")
                    table_to_reserve.reserve(customer_name, reservation_time)
                    print(f"✅ Table {table_to_reserve.table_number} has been reserved for {customer_name} at {reservation_time}.")
                    break
                else:
                    print("Invalid table number. Please choose from the available tables.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def view_table_reservations(self):
        print("\n--- Table Reservations ---")
        if not any(table.is_reserved for table in self.tables):
            print("No tables are currently reserved.")
        else:
            for table in self.tables:
                if table.is_reserved:
                    print(table)

    def unreserve_table(self):
        print("\n--- Unreserve Table ---")
        reserved_tables = [table for table in self.tables if table.is_reserved]
        if not reserved_tables:
            print("No tables are currently reserved.")
            return
        print("Currently Reserved Tables:")
        for table in reserved_tables:
            print(f"- Table {table.table_number} (Reserved by: {table.reserved_by} at {table.reservation_time})")
        while True:
            try:
                table_number_to_unreserve = int(input("Enter the table number to unreserve: "))
                table_to_unreserve = next((table for table in reserved_tables if table.table_number == table_number_to_unreserve), None)
                if table_to_unreserve:
                    table_to_unreserve.unreserve()
                    print(f"✅ Table {table_to_unreserve.table_number} has been unreserved.")
                    break
                else:
                    print("Invalid table number or table is not currently reserved.")
            except ValueError:
                print("Invalid input. Please enter a number.")