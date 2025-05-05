from datetime import datetime

DINE_IN_ORDER = "Dine-In"
TAKEAWAY_ORDER = "Takeaway"
DELIVERY_ORDER = "Home Delivery"

class Order:
    def __init__(self, order_type, table=None):
        self.order_type = order_type
        self.table = table
        self.items = []
        self.total =0.0
        self.payment_method = None

    def add_item(self, item):
        self.items.append(item)
        self.total=sum(i.price for i in self.items)
    def choose_payment_method(self):
        print("\nChoose payment method:")
        print("1. Credit Card")
        print("2. Cash")
        choice = input("Enter choice: ")
        if choice == '1':
            self.payment_method = "Credit Card"
        elif choice == '2':
            self.payment_method = "Cash"
        else:
            print("Invalid choice.")
            self.choose_payment_method()
                        
    def show_order(self):
        print(f"\n--- {self.order_type} Order ---")
        if self.order_type == DINE_IN_ORDER and self.table:
            print(f"Table Number: {self.table.table_number}")
        for item in self.items:
            print(f"- {item.name}: ${item.price:.2f}")
        print(f"Total: ${self.total:.2f} \nPayment Method: {self.payment_method}")
    def generate_receipt(self, restaurant_name, amount_paid=None):
        print(f"\n--- Receipt from {restaurant_name} ---")
        self.show_order()
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if amount_paid is not None and self.payment_method == "Cash":
            change=amount_paid - self.total
            print(f"Amount Paid: ${amount_paid:.2f}")
            if change >= 0:
                print(f"Change: ${change:.2f}")
            else:
                print("Insufficient amount paid.")
        print("Thank you for dining with us!\n")