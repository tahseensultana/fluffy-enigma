import Order

DINE_IN_ORDER = "Dine-In"
TAKEAWAY_ORDER = "Takeaway"
DELIVERY_ORDER = "Home Delivery"

class OrderService:
    def __init__(self, menu_service, table_service):
        self.menu_service = menu_service
        self.table_service = table_service

    def take_order(self, user):
        print("\n--- Take Order ---")
        dietary_preferences = self.menu_service.get_dietary_preferences()
        print("\nSelect Order Type:")
        print(f"1. {DINE_IN_ORDER}")
        print(f"2. {TAKEAWAY_ORDER}")
        print(f"3. {DELIVERY_ORDER}")
        order_type_choice = input("Choose option: ")
        if order_type_choice == '1':
            order_type = DINE_IN_ORDER
            table = self.table_service.select_table()
        elif order_type_choice == '2':
            order_type = TAKEAWAY_ORDER
            table = None        
        elif order_type_choice == '3':  
            order_type = DELIVERY_ORDER
            table = None
        else:
            print("Invalid choice. Please select a valid order type.")
            return    
        order = Order.Order(order_type, table)
        while True:
            item_name = input("Enter item name (or 'done' to finish): ")
            if item_name.lower() == 'done':
                break
            item = next((item for item in self.menu_service.menu if item.name.lower() == item_name.lower()), None)
            if item:
                order.add_item(item)
            else:
                print("Item not found. Please select from the menu.")
        order.choose_payment_method()
        order.show_order()
        if order.payment_method == "Cash":
            while True:
                try:
                    amount_paid = float(input("Enter amount paid by customer: $"))
                    order.generate_receipt("MIU Diner", amount_paid)
                    return
                except ValueError:
                    print("Invalid input. Please enter a numerical value for the amount paid.")          
        else:
            order.generate_receipt("MIU Diner") 