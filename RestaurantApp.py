import User
import MenuItem
import MenuService
import TableService
import OrderService
import EventService
from User import UserService 

class RestaurantApp:
    def __init__(self):
        self.users=UserService()
        self.menu_items = [
            MenuItem.MenuItem("French Fries", 2.50, "Appetizer", dietary_tags=["Vegetarian", "Vegan"]),
            MenuItem.MenuItem("Vegetarian Burger", 6.99, "Main Course", dietary_tags=["Vegetarian"]),
            MenuItem.MenuItem("Vegan Pizza", 9.99, "Main Course", dietary_tags=["Vegan"]),
            MenuItem.MenuItem("Beef Burger", 7.99, "Main Course"),
            MenuItem.MenuItem("Chicken Nugget", 3.50, "Appetizer"),
            MenuItem.MenuItem("Chicken Pizza", 8.99, "Main Course"),
            MenuItem.MenuItem("Onion Rings",3.00, "Appetizer", dietary_tags=["Vegetarian", "Vegan"]),
            MenuItem.MenuItem("Caesar Salad", 5.50, "Appetizer", dietary_tags=["Vegetarian"]),
            MenuItem.MenuItem("Alfredo Pasta",6.50, "Main Course", dietary_tags=["Vegetarian"]),
            MenuItem.MenuItem("Soda",2.00, "Drinks"),
            MenuItem.MenuItem("Iced Coffee",2.99, "Drinks"),
            MenuItem.MenuItem("Water", 1.00, "Drinks"),
        ]
        self.menu_service= MenuService.MenuService(self.menu_items)
        self.table_service = TableService.TableService()
        self.order_service = OrderService.OrderService(self.menu_service, self.table_service)
        self.event_service = EventService.EventService()
        self.restaurant_name = "MIU Diner" 
   
    def start(self):
        while True:
            print(f"Welcome to {self.restaurant_name}!")
            print("1. Login")
            print("2. Exit")
            choice = input("Choose an option: ")
            if choice == '1':
                username = input("Username: ")
                password = input("Password: ")
                user = self.users.authenticate(username, password)
                if user:
                    print(f"Login successful! Welcome {user._role}.")
                    print(f"\n--- {self.restaurant_name} | Logged in as {user._role} ---")
                    while user.show_options(self):
                        pass
                else:
                    print("Invalid username or password. Please try again.")
            elif choice == '2':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")            


if __name__ == "__main__":
    app = RestaurantApp()
    app.start() 
