ADMIN_ROLE = "Admin"
STAFF_ROLE = "Staff"
CUSTOMER_ROLE = "Customer"

import MenuItem

class User:
    def __init__(self, username, password, role):
        self._username = username
        self._password = password
        self._role = role

    def __str__(self):
        return f"User: {self.get_username()} (Role: {self.get_role()})"

    def get_username(self):
        return self._username

    def get_role(self):
        return self._role

    def show_options(self, app):
        pass


class Admin(User):
    def __init__(self, username, password):
        super().__init__(username, password, ADMIN_ROLE)

    def show_options(self, app):
        while True:
            print("1. Add Menu Item\n2. Remove Menu Item\n3. Show Menu\n4. Show Event Reservations\n5. View Table Reservations\n6. Unreserve Table\n7. Logout")
            choice = input("Choose an option: ")
            if choice == '1':
                name = input("Enter item name: ")
                price = float(input("Enter price: "))
                category = input("Enter category (e.g., Appetizer, Main Course, Drinks): ")
                dietary_tags = input("Enter dietary tags (comma-separated): ").split(',')
                dietary_tags = [tag.strip() for tag in dietary_tags]
                app.menu_service.add_item(MenuItem.MenuItem(name, price, category, dietary_tags))
                print("Item added!")
            elif choice == '2':
                name = input("Enter item name to remove: ")
                app.menu_service.remove_item(name)
                print("Item removed.")
            elif choice == '3':
                app.menu_service.show_menu()
            elif choice == '4':
                app.event_service.show_event_reservations()
            elif choice == '5':
                app.table_service.view_table_reservations()
            elif choice == '6':
                app.table_service.unreserve_table()
            elif choice == '7':
                print("Logging out...")
                break
            else:
                print("Invalid choice.")


class Staff(User):
    def __init__(self, username, password):
        super().__init__(username, password, STAFF_ROLE)

    def show_options(self, app):
        while True:
            print("1. Take Order\n2. Show Menu\n3. Show Event Reservations\n4. Reserve Table\n5. View Table Reservations\n6. Logout")
            choice = input("Choose an option: ")
            if choice == '1':
                app.order_service.take_order(self)
            elif choice == '2':
                app.menu_service.show_menu()
            elif choice == '3':
                app.event_service.show_event_reservations()
            elif choice == '4':
                app.table_service.reserve_table()
            elif choice == '5':
                app.table_service.view_table_reservations()
            elif choice == '6':
                print("Logging out...")
                break
            else:
                print("Invalid choice.")


class Customer(User):
    def __init__(self, username, password):
        super().__init__(username, password, CUSTOMER_ROLE)

    def show_options(self, app):
        while True:
            print("1. Show Menu\n2. Place Order\n3. Reserve Event\n4. Reserve Table\n5. Logout")
            choice = input("Choose an option: ")
            if choice == '1':
                app.menu_service.show_menu()
            elif choice == '2':
                app.order_service.take_order(self)
            elif choice == '3':
                app.event_service.make_event_reservation()
            elif choice == '4':
                app.table_service.reserve_table()
            elif choice == '5':
                print("Logging out...")
                break
            else:
                print("Invalid choice.")
                
class UserService:
    def __init__(self):
        self.users = [
            Admin("admin1", "adminpass"),
            Staff("staff1", "staffpass"),
            Customer("cust1", "custpass")
        ]
    
    def authenticate(self, username, password):
        for user in self.users:
            if user.get_username() == username and user._password == password:
                return user
        return None                 