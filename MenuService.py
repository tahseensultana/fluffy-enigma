class MenuService:
    def __init__(self, menu=None):
        self.menu = menu if menu else []

    def add_item(self, item):
        self.menu.append(item)

    def remove_item(self, item_name):
        self.menu = [item for item in self.menu if item.name != item_name]

    def show_menu(self, dietary_preferences=None):
        categorized_menu = {}
        for item in self.menu:
            categorized_menu.setdefault(item.category, []).append(item)
        print("\n--- Menu ---")
        for category, items in categorized_menu.items():
            print(f"\n--- {category} ---")
            for item in items:
                dietory_info = f" | Dietary: {', '.join(item.dietary_tags)}" if item.dietary_tags else " "
                print(f"- {item.name:<15} ${item.price:.2f} {dietory_info}")
            
        if dietary_preferences:
            filtered_menu= [item for item in self.menu if item.is_compatible_with(dietary_preferences)]
            for item in filtered_menu:
                dietory_info = f" | Dietary: {', '.join(item.dietary_tags)}" if item.dietary_tags else " "
                print(f"- {item.name:<15} ${item.price:.2f} {dietory_info}")
                        
    def get_dietary_preferences(self):
        dietary_options = ["Vegetarian", "Vegan", "None"]
        print("\nSelect your dietary preferences:")
        for i, option in enumerate(dietary_options, start=1):
            print(f"{i}. {option}")
        choice = input("Enter your choice (e.g., 1 for Vegetarian): ")
        preferences = []
        if choice == '1':
            preferences.append("Vegetarian")
        elif choice == '2':
            preferences.append("Vegan")
        elif choice == '3':
            print("No dietary preferences selected.")
        else:
            print("Invalid choice.")
        return preferences
