# streamlit code
import streamlit as st
import hashlib
from datetime import datetime
from typing import Dict, List, Optional

# Original classes remain largely the same
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
        # Initialize system if not already in session state
        if 'users' not in st.session_state:
            st.session_state.users = {}
            st.session_state.products = {}
            st.session_state.current_user = None
            st.session_state.stock_threshold = 5
            self._initialize_system()
        
        # Reference session state
        self.users = st.session_state.users
        self.products = st.session_state.products
        self.current_user = st.session_state.current_user
        self.stock_threshold = st.session_state.stock_threshold

    def _initialize_system(self):
        self.add_user("admin", "admin123", "Admin")
        self.add_user("user", "user123", "User")

    # Rest of the methods remain similar but use session state
    def add_user(self, username: str, password: str, role: str) -> bool:
        if username not in st.session_state.users:
            st.session_state.users[username] = User(username, password, role)
            return True
        return False

    def login(self, username: str, password: str) -> bool:
        if username in st.session_state.users and st.session_state.users[username].check_password(password):
            st.session_state.current_user = st.session_state.users[username]
            return True
        return False

    def logout(self):
        st.session_state.current_user = None

    def add_product(self, name: str, category: str, price: float, stock_quantity: int) -> bool:
        if not st.session_state.current_user or st.session_state.current_user.role != "Admin":
            raise PermissionError("Only admins can add products")
        
        product_id = len(st.session_state.products) + 1
        st.session_state.products[product_id] = Product(product_id, name, category, price, stock_quantity)
        return True

    def update_product(self, product_id: int, **kwargs) -> bool:
        if not st.session_state.current_user or st.session_state.current_user.role != "Admin":
            raise PermissionError("Only admins can update products")
        
        if product_id not in st.session_state.products:
            raise ValueError("Product not found")
        
        product = st.session_state.products[product_id]
        for key, value in kwargs.items():
            if value is not None:
                setattr(product, key, value)
        product.last_updated = datetime.now()
        return True

    def delete_product(self, product_id: int) -> bool:
        if not st.session_state.current_user or st.session_state.current_user.role != "Admin":
            raise PermissionError("Only admins can delete products")
        
        if product_id not in st.session_state.products:
            raise ValueError("Product not found")
        
        del st.session_state.products[product_id]
        return True

    def get_low_stock_products(self) -> List[Product]:
        return [product for product in st.session_state.products.values()
                if product.stock_quantity <= self.stock_threshold]

    def search_products(self, search_term: str) -> List[Product]:
        search_term = search_term.lower()
        return [product for product in st.session_state.products.values()
                if search_term in product.name.lower() or 
                search_term in product.category.lower()]

def main():
    st.set_page_config(page_title="Inventory Management System", layout="wide")
    st.title("Inventory Management System")

    # Initialize system
    inventory = InventorySystem()

    # Login/Logout section
    with st.sidebar:
        if st.session_state.current_user is None:
            st.header("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                try:
                    if inventory.login(username, password):
                        st.success(f"Welcome, {username}!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.write(f"Logged in as: {st.session_state.current_user.username}")
            st.write(f"Role: {st.session_state.current_user.role}")
            if st.button("Logout"):
                inventory.logout()
                st.rerun()

    # Main content
    if st.session_state.current_user is not None:
        # Tabs for different functions
        tab1, tab2, tab3 = st.tabs(["Products", "Search", "Low Stock"])

        with tab1:
            st.header("Products")
            
            # Admin functions
            if st.session_state.current_user.role == "Admin":
                with st.expander("Add New Product"):
                    col1, col2 = st.columns(2)
                    with col1:
                        name = st.text_input("Product Name")
                        category = st.text_input("Category")
                    with col2:
                        price = st.number_input("Price", min_value=0.0, step=0.01)
                        stock = st.number_input("Stock Quantity", min_value=0, step=1)
                    
                    if st.button("Add Product"):
                        try:
                            if inventory.add_product(name, category, price, stock):
                                st.success("Product added successfully!")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

            # Display products table
            if st.session_state.products:
                product_data = []
                for product in st.session_state.products.values():
                    product_data.append({
                        "ID": product.product_id,
                        "Name": product.name,
                        "Category": product.category,
                        "Price": f"${product.price:.2f}",
                        "Stock": product.stock_quantity,
                        "Last Updated": product.last_updated.strftime("%Y-%m-%d %H:%M")
                    })
                
                st.dataframe(product_data)
                
                # Admin edit/delete functions
                if st.session_state.current_user.role == "Admin":
                    with st.expander("Edit/Delete Product"):
                        product_id = st.number_input("Product ID", min_value=1, step=1)
                        if st.button("Delete Product"):
                            try:
                                if inventory.delete_product(product_id):
                                    st.success("Product deleted successfully!")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                        
                        # Edit form
                        new_name = st.text_input("New Name (optional)")
                        new_category = st.text_input("New Category (optional)")
                        new_price = st.number_input("New Price (optional)", min_value=0.0, step=0.01)
                        new_stock = st.number_input("New Stock Quantity (optional)", min_value=0, step=1)
                        
                        if st.button("Update Product"):
                            try:
                                updates = {}
                                if new_name:
                                    updates['name'] = new_name
                                if new_category:
                                    updates['category'] = new_category
                                if new_price > 0:
                                    updates['price'] = new_price
                                if new_stock >= 0:
                                    updates['stock_quantity'] = new_stock
                                
                                if inventory.update_product(product_id, **updates):
                                    st.success("Product updated successfully!")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
            else:
                st.info("No products in inventory")

        with tab2:
            st.header("Search Products")
            search_term = st.text_input("Enter search term")
            if search_term:
                results = inventory.search_products(search_term)
                if results:
                    search_data = []
                    for product in results:
                        search_data.append({
                            "ID": product.product_id,
                            "Name": product.name,
                            "Category": product.category,
                            "Price": f"${product.price:.2f}",
                            "Stock": product.stock_quantity
                        })
                    st.dataframe(search_data)
                else:
                    st.info("No products found")

        with tab3:
            st.header("Low Stock Products")
            low_stock = inventory.get_low_stock_products()
            if low_stock:
                low_stock_data = []
                for product in low_stock:
                    low_stock_data.append({
                        "ID": product.product_id,
                        "Name": product.name,
                        "Category": product.category,
                        "Stock": product.stock_quantity
                    })
                st.dataframe(low_stock_data)
            else:
                st.info("No products with low stock")

if __name__ == "__main__":
    main()