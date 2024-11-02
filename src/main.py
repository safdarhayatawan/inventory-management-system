import hashlib
from datetime import datetime
from typing import List, Dict, Optional

class User:
    def __init__(self, username: str, password: str, role: str):
        self.username = username
        self.password = self._hash_password(password)
        self.role = role

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password: str) -> bool:
        return self._hash_password(password) == self.password

class Product:
    def __init__(self, product_id: int, name: str, category: str, price: float, stock_quantity: int):
        self.product_id = product_id
        self.name = name
        self.category = category
        self.price = price
        self.stock_quantity = stock_quantity
        self.last_updated = datetime.now()

    def update_stock(self, quantity: int):
        self.stock_quantity = quantity
        self.last_updated = datetime.now()

class InventorySystem:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.products: Dict[int, Product] = {}
        self.current_user: Optional[User] = None
        self.stock_threshold = 5
        self._initialize_system()

    def _initialize_system(self):
        # Create default admin user
        self.add_user("admin", "admin123", "Admin")
        # Create default regular user
        self.add_user("user", "user123", "User")

    def add_user(self, username: str, password: str, role: str) -> bool:
        if username not in self.users:
            self.users[username] = User(username, password, role)
            return True
        return False

    def login(self, username: str, password: str) -> bool:
        if username in self.users and self.users[username].check_password(password):
            self.current_user = self.users[username]
            return True
        return False

    def add_product(self, name: str, category: str, price: float, stock_quantity: int) -> bool:
        if not self.current_user or self.current_user.role != "Admin":
            raise PermissionError("Only admins can add products")
        
        product_id = len(self.products) + 1
        self.products[product_id] = Product(product_id, name, category, price, stock_quantity)
        return True

    def update_product(self, product_id: int, name: str = None, category: str = None, 
                      price: float = None, stock_quantity: int = None) -> bool:
        if not self.current_user or self.current_user.role != "Admin":
            raise PermissionError("Only admins can update products")
        
        if product_id not in self.products:
            raise ValueError("Product not found")
        
        product = self.products[product_id]
        if name is not None:
            product.name = name
        if category is not None:
            product.category = category
        if price is not None:
            product.price = price
        if stock_quantity is not None:
            product.stock_quantity = stock_quantity
            
        product.last_updated = datetime.now()
        return True

    def delete_product(self, product_id: int) -> bool:
        if not self.current_user or self.current_user.role != "Admin":
            raise PermissionError("Only admins can delete products")
        
        if product_id not in self.products:
            raise ValueError("Product not found")
        
        del self.products[product_id]
        return True

    def get_product(self, product_id: int) -> Optional[Product]:
        return self.products.get(product_id)

    def search_products(self, search_term: str) -> List[Product]:
        search_term = search_term.lower()
        return [product for product in self.products.values()
                if search_term in product.name.lower() or 
                search_term in product.category.lower()]

    def get_low_stock_products(self) -> List[Product]:
        return [product for product in self.products.values()
                if product.stock_quantity <= self.stock_threshold]

def main():
    inventory = InventorySystem()
    
    while True:
        if not inventory.current_user:
            print("\n=== Inventory Management System ===")
            print("1. Login")
            print("2. Exit")
            
            choice = input("Enter your choice (1-2): ")
            
            if choice == "1":
                username = input("Username: ")
                password = input("Password: ")
                
                try:
                    if inventory.login(username, password):
                        print(f"\nWelcome, {username}!")
                    else:
                        print("Invalid credentials!")
                except Exception as e:
                    print(f"Error: {str(e)}")
            
            elif choice == "2":
                print("Goodbye!")
                break
        
        else:
            print(f"\n=== Welcome {inventory.current_user.username} ({inventory.current_user.role}) ===")
            print("1. View all products")
            print("2. Search products")
            print("3. View low stock products")
            
            if inventory.current_user.role == "Admin":
                print("4. Add product")
                print("5. Update product")
                print("6. Delete product")
            
            print("7. Logout")
            
            choice = input("Enter your choice: ")
            
            try:
                if choice == "1":
                    if not inventory.products:
                        print("No products found!")
                    else:
                        print("\nProduct List:")
                        for product in inventory.products.values():
                            print(f"ID: {product.product_id}, Name: {product.name}, "
                                  f"Category: {product.category}, Price: ${product.price}, "
                                  f"Stock: {product.stock_quantity}")
                
                elif choice == "2":
                    search_term = input("Enter search term: ")
                    results = inventory.search_products(search_term)
                    if results:
                        print("\nSearch Results:")
                        for product in results:
                            print(f"ID: {product.product_id}, Name: {product.name}, "
                                  f"Category: {product.category}, Stock: {product.stock_quantity}")
                    else:
                        print("No products found!")
                
                elif choice == "3":
                    low_stock = inventory.get_low_stock_products()
                    if low_stock:
                        print("\nLow Stock Products:")
                        for product in low_stock:
                            print(f"ID: {product.product_id}, Name: {product.name}, "
                                  f"Stock: {product.stock_quantity}")
                    else:
                        print("No low stock products!")
                
                elif choice == "4" and inventory.current_user.role == "Admin":
                    name = input("Product name: ")
                    category = input("Category: ")
                    price = float(input("Price: "))
                    stock = int(input("Initial stock: "))
                    
                    if inventory.add_product(name, category, price, stock):
                        print("Product added successfully!")
                
                elif choice == "5" and inventory.current_user.role == "Admin":
                    product_id = int(input("Enter product ID to update: "))
                    name = input("New name (press enter to skip): ")
                    category = input("New category (press enter to skip): ")
                    price = input("New price (press enter to skip): ")
                    stock = input("New stock quantity (press enter to skip): ")
                    
                    updates = {}
                    if name:
                        updates['name'] = name
                    if category:
                        updates['category'] = category
                    if price:
                        updates['price'] = float(price)
                    if stock:
                        updates['stock_quantity'] = int(stock)
                    
                    if inventory.update_product(product_id, **updates):
                        print("Product updated successfully!")
                
                elif choice == "6" and inventory.current_user.role == "Admin":
                    product_id = int(input("Enter product ID to delete: "))
                    if inventory.delete_product(product_id):
                        print("Product deleted successfully!")
                
                elif choice == "7":
                    inventory.current_user = None
                    print("Logged out successfully!")
                
                else:
                    print("Invalid choice!")
            
            except ValueError as e:
                print(f"Invalid input: {str(e)}")
            except PermissionError as e:
                print(f"Permission denied: {str(e)}")
            except Exception as e:
                print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()