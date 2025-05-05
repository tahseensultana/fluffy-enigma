class MenuItem:
    def __init__(self, name, price, category, dietary_tags=None):
        self.name = name
        self.price = price
        self.category = category
        self.dietary_tags = dietary_tags if dietary_tags else []
    
    def __str__(self):
        dietary_info = ", ".join(self.dietary_tags) if self.dietary_tags else "No dietary information"
        return f"{self.name}: ${self.price:.2f} | Dietary: {dietary_info}"

    def is_compatible_with(self, dietary_preferences):
        return any(tag in self.dietary_tags for tag in dietary_preferences)
