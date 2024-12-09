import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Initialize the database
def initialize_db():
    conn = sqlite3.connect("ice_cream_parlor.db")
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS SeasonalFlavors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        available BOOLEAN
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Ingredients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        quantity INTEGER
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS CustomerAllergies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        allergy TEXT UNIQUE
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        flavor_id INTEGER,
        FOREIGN KEY (flavor_id) REFERENCES SeasonalFlavors(id)
    )
    """)

    # Insert default values into SeasonalFlavors
    cursor.execute("""
    INSERT OR IGNORE INTO SeasonalFlavors (name, description, available)
    VALUES
    ('Vanilla', 'Classic vanilla flavor with a creamy taste', 1),
    ('Chocolate', 'Rich chocolate flavor with a smooth texture', 1),
    ('Strawberry', 'Fresh strawberry ice cream with real fruit chunks', 1),
    ('Mango', 'Tropical mango ice cream with a tangy twist', 1)
    """)

    conn.commit()
    conn.close()


# Add a new allergy
# Add a new allergy and refresh the page
def add_allergy(allergy, refresh_callback=None):
    if not allergy.strip():
        messagebox.showwarning("Warning", "Allergy name cannot be empty.")
        return
    conn = sqlite3.connect("ice_cream_parlor.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO CustomerAllergies (allergy) VALUES (?)", (allergy,))
        conn.commit()
        messagebox.showinfo("Success", "Allergy added successfully!")
        if refresh_callback:
            refresh_callback()  # Refresh the allergy page
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Failed to add allergy: {e}")
    finally:
        conn.close()


# Remove an allergy
def remove_allergy(allergy_id, refresh_callback):
    conn = sqlite3.connect("ice_cream_parlor.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM CustomerAllergies WHERE id = ?", (allergy_id,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Allergy removed successfully!")
    refresh_callback()  # Refresh the allergies list on the UI


# Fetch flavors excluding those that match user allergies
def fetch_filtered_flavors():
    conn = sqlite3.connect("ice_cream_parlor.db")
    cursor = conn.cursor()

    # Get all allergies
    cursor.execute("SELECT allergy FROM CustomerAllergies")
    allergies = [row[0].lower() for row in cursor.fetchall()]

    # Fetch flavors that do not contain allergens
    if allergies:
        query = "SELECT id, name, description FROM SeasonalFlavors WHERE available = 1 AND " + \
                " AND ".join(["LOWER(name) NOT LIKE ?"] * len(allergies))
        flavors = cursor.execute(query, [f"%{allergy}%" for allergy in allergies]).fetchall()
    else:
        flavors = cursor.execute("SELECT id, name, description FROM SeasonalFlavors WHERE available = 1").fetchall()

    conn.close()
    return flavors

# Add a flavor to the cart
def add_to_cart(flavor_id):
    conn = sqlite3.connect("ice_cream_parlor.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Cart (flavor_id) VALUES (?)", (flavor_id,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Added to cart!")

# Remove a flavor from the cart
def remove_from_cart(cart_id, refresh_callback):
    conn = sqlite3.connect("ice_cream_parlor.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Cart WHERE id = ?", (cart_id,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Item removed from cart!")
    refresh_callback()  # Refresh the cart items on the UI


# Main application class
class IceCreamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ice Cream Parlor Cafe")
        self.root.geometry("600x400")
        self.create_main_menu()

    def create_main_menu(self):
        self.clear_frame()

        ttk.Label(self.root, text="Welcome to the Ice Cream Parlor", font=("Arial", 16)).pack(pady=20)
        ttk.Button(self.root, text="View Seasonal Flavors", command=self.view_flavors).pack(pady=10)
        ttk.Button(self.root, text="Manage Cart", command=self.view_cart).pack(pady=10)
        ttk.Button(self.root, text="Manage Allergies", command=self.manage_allergies_page).pack(pady=10)

    def view_flavors(self):
        self.clear_frame()
        flavors = fetch_filtered_flavors()

        ttk.Label(self.root, text="Seasonal Flavors", font=("Arial", 16)).pack(pady=10)
        for flavor in flavors:
            frame = ttk.Frame(self.root)
            frame.pack(pady=5)
            ttk.Label(frame, text=f"{flavor[1]}: {flavor[2]}").pack(side="left")
            ttk.Button(frame, text="Add to Cart", command=lambda f=flavor[0]: add_to_cart(f)).pack(side="right")

        ttk.Button(self.root, text="Back to Main Menu", command=self.create_main_menu).pack(pady=20)

    def view_cart(self):
        self.clear_frame()

        ttk.Label(self.root, text="Cart Items", font=("Arial", 16)).pack(pady=10)

        def refresh_cart():
            self.view_cart()  # Re-render the cart view

        conn = sqlite3.connect("ice_cream_parlor.db")
        cursor = conn.cursor()
        cursor.execute("""
        SELECT Cart.id, SeasonalFlavors.name FROM Cart
        JOIN SeasonalFlavors ON Cart.flavor_id = SeasonalFlavors.id
        """)
        items = cursor.fetchall()
        conn.close()

        for item in items:
            frame = ttk.Frame(self.root)
            frame.pack(pady=5)
            ttk.Label(frame, text=item[1]).pack(side="left")
            ttk.Button(frame, text="Remove", command=lambda c=item[0]: remove_from_cart(c, refresh_cart)).pack(side="right")

        ttk.Button(self.root, text="Back to Main Menu", command=self.create_main_menu).pack(pady=20)


    def manage_allergies_page(self):
        self.clear_frame()

        ttk.Label(self.root, text="Manage Allergies", font=("Arial", 16)).pack(pady=10)

    # Display existing allergies
        conn = sqlite3.connect("ice_cream_parlor.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, allergy FROM CustomerAllergies")
        allergies = cursor.fetchall()
        conn.close()

        def refresh_allergies():
            self.manage_allergies_page()  # Re-render the allergies view

        for allergy in allergies:
            frame = ttk.Frame(self.root)
            frame.pack(pady=5)
            ttk.Label(frame, text=allergy[1]).pack(side="left")
            ttk.Button(frame, text="Remove", command=lambda a=allergy[0]: remove_allergy(a, refresh_allergies)).pack(side="right")
    
    # Add new allergy
        ttk.Label(self.root, text="Add New Allergy:").pack(pady=10)
        entry = ttk.Entry(self.root)
        entry.pack(pady=5)
        ttk.Button(self.root, text="Add", command=lambda: add_allergy(entry.get(), refresh_callback=refresh_allergies)).pack(pady=10)
        ttk.Button(self.root, text="Back to Main Menu", command=self.create_main_menu).pack(pady=20)


    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# Initialize and run the app
if __name__ == "__main__":
    initialize_db()
    root = tk.Tk()
    app = IceCreamApp(root)
    root.mainloop()
