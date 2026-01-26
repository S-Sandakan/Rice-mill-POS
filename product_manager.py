"""
Rice Mill POS System - Product Management Module
Handles adding, editing, and managing rice products
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import db


class ProductManagerWindow:
    """Product Management Window"""
    
    def __init__(self, parent, user_data):
        self.window = tk.Toplevel(parent)
        self.window.title("Product Management")
        self.window.geometry("1000x600")
        self.user_data = user_data
        
        self.create_widgets()
        self.load_products()
    
    def create_widgets(self):
        """Create product management widgets"""
        # Header
        header = tk.Label(
            self.window,
            text="🌾 Product Management",
            font=("Arial", 16, "bold"),
            bg="#2c3e50",
            fg="white",
            pady=10
        )
        header.pack(fill=tk.X)
        
        # Main frame
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Products list frame
        list_frame = tk.LabelFrame(main_frame, text="Products", font=("Arial", 12, "bold"))
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create treeview
        columns = ('code', 'name', 'quality', 'price_kg', 'bag_size', 'price_bag', 'active')
        self.products_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        self.products_tree.heading('code', text='Product Code')
        self.products_tree.heading('name', text='Product Name')
        self.products_tree.heading('quality', text='Quality')
        self.products_tree.heading('price_kg', text='Price/kg (₹)')
        self.products_tree.heading('bag_size', text='Bag Size (kg)')
        self.products_tree.heading('price_bag', text='Price/Bag (₹)')
        self.products_tree.heading('active', text='Status')
        
        self.products_tree.column('code', width=120)
        self.products_tree.column('name', width=200)
        self.products_tree.column('quality', width=100)
        self.products_tree.column('price_kg', width=100)
        self.products_tree.column('bag_size', width=100)
        self.products_tree.column('price_bag', width=120)
        self.products_tree.column('active', width=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar.set)
        
        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        tk.Button(
            buttons_frame,
            text="➕ Add Product",
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=8,
            command=self.add_product_dialog
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            buttons_frame,
            text="✏️ Edit Product",
            font=("Arial", 11, "bold"),
            bg="#3498db",
            fg="white",
            padx=20,
            pady=8,
            command=self.edit_product_dialog
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            buttons_frame,
            text="🔄 Refresh",
            font=("Arial", 11),
            bg="#95a5a6",
            fg="white",
            padx=20,
            pady=8,
            command=self.load_products
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            buttons_frame,
            text="Close",
            font=("Arial", 11),
            padx=20,
            pady=8,
            command=self.window.destroy
        ).pack(side=tk.RIGHT, padx=5)
    
    def load_products(self):
        """Load products into treeview"""
        # Clear existing data
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # Load from database
        products = db.fetch_all("SELECT * FROM products ORDER BY name")
        
        for product in products:
            self.products_tree.insert('', tk.END, values=(
                product['product_code'],
                product['name'],
                product['quality'].title(),
                f"{product['price_per_kg']:.2f}",
                f"{product['bag_size_kg']:.1f}" if product['bag_size_kg'] else "N/A",
                f"{product['price_per_bag']:.2f}" if product['price_per_bag'] else "N/A",
                "Active" if product['is_active'] else "Inactive"
            ))
    
    def add_product_dialog(self):
        """Show add product dialog"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Add New Product")
        dialog.geometry("500x550")
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Title
        tk.Label(
            dialog,
            text="➕ Add New Product",
            font=("Arial", 14, "bold")
        ).pack(pady=15)
        
        # Form frame
        form_frame = tk.Frame(dialog, padx=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Product Code
        tk.Label(form_frame, text="Product Code:", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=8)
        code_entry = tk.Entry(form_frame, font=("Arial", 11), width=25)
        code_entry.grid(row=0, column=1, pady=8, sticky="ew")
        
        # Product Name
        tk.Label(form_frame, text="Product Name:", font=("Arial", 11)).grid(row=1, column=0, sticky="w", pady=8)
        name_entry = tk.Entry(form_frame, font=("Arial", 11), width=25)
        name_entry.grid(row=1, column=1, pady=8, sticky="ew")
        
        # Quality
        tk.Label(form_frame, text="Quality:", font=("Arial", 11)).grid(row=2, column=0, sticky="w", pady=8)
        quality_var = tk.StringVar(value="standard")
        quality_frame = tk.Frame(form_frame)
        quality_frame.grid(row=2, column=1, sticky="w", pady=8)
        
        tk.Radiobutton(quality_frame, text="Premium", variable=quality_var, value="premium").pack(side=tk.LEFT)
        tk.Radiobutton(quality_frame, text="Standard", variable=quality_var, value="standard").pack(side=tk.LEFT)
        tk.Radiobutton(quality_frame, text="Economic", variable=quality_var, value="economic").pack(side=tk.LEFT)
        
        # Price per KG
        tk.Label(form_frame, text="Price per KG (₹):", font=("Arial", 11)).grid(row=3, column=0, sticky="w", pady=8)
        price_kg_entry = tk.Entry(form_frame, font=("Arial", 11), width=25)
        price_kg_entry.grid(row=3, column=1, pady=8, sticky="ew")
        
        # Bag Size
        tk.Label(form_frame, text="Bag Size (kg):", font=("Arial", 11)).grid(row=4, column=0, sticky="w", pady=8)
        bag_size_entry = tk.Entry(form_frame, font=("Arial", 11), width=25)
        bag_size_entry.grid(row=4, column=1, pady=8, sticky="ew")
        bag_size_entry.insert(0, "25.0")
        
        # Price per Bag
        tk.Label(form_frame, text="Price per Bag (₹):", font=("Arial", 11)).grid(row=5, column=0, sticky="w", pady=8)
        price_bag_entry = tk.Entry(form_frame, font=("Arial", 11), width=25)
        price_bag_entry.grid(row=5, column=1, pady=8, sticky="ew")
        
        # Description
        tk.Label(form_frame, text="Description:", font=("Arial", 11)).grid(row=6, column=0, sticky="nw", pady=8)
        desc_text = tk.Text(form_frame, font=("Arial", 10), width=25, height=4)
        desc_text.grid(row=6, column=1, pady=8, sticky="ew")
        
        form_frame.columnconfigure(1, weight=1)
        
        def save_product():
            try:
                code = code_entry.get().strip()
                name = name_entry.get().strip()
                quality = quality_var.get()
                price_kg = float(price_kg_entry.get())
                
                if not code or not name:
                    messagebox.showerror("Error", "Product code and name are required")
                    return
                
                if price_kg <= 0:
                    messagebox.showerror("Error", "Price per kg must be greater than 0")
                    return
                
                # Optional fields
                bag_size = None
                price_bag = None
                
                if bag_size_entry.get().strip():
                    bag_size = float(bag_size_entry.get())
                
                if price_bag_entry.get().strip():
                    price_bag = float(price_bag_entry.get())
                
                description = desc_text.get("1.0", tk.END).strip()
                
                # Add product to database
                product_id = db.add_product(
                    product_code=code,
                    name=name,
                    quality=quality,
                    price_per_kg=price_kg,
                    bag_size_kg=bag_size,
                    price_per_bag=price_bag,
                    description=description or None
                )
                
                if product_id:
                    messagebox.showinfo("Success", f"Product '{name}' added successfully!")
                    dialog.destroy()
                    self.load_products()
                else:
                    messagebox.showerror("Error", "Failed to add product")
            
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for prices")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {str(e)}")
        
        # Buttons
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame,
            text="Save Product",
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            padx=30,
            pady=8,
            command=save_product
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            font=("Arial", 11),
            padx=30,
            pady=8,
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
        
        code_entry.focus()
    
    def edit_product_dialog(self):
        """Show edit product dialog"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to edit")
            return
        
        # Get selected product data
        item_values = self.products_tree.item(selection[0])['values']
        product_code = item_values[0]
        
        # Get full product from database
        product = db.fetch_one("SELECT * FROM products WHERE product_code = ?", (product_code,))
        
        if not product:
            messagebox.showerror("Error", "Product not found")
            return
        
        # Create dialog
        dialog = tk.Toplevel(self.window)
        dialog.title("Edit Product")
        dialog.geometry("500x550")
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Title
        tk.Label(
            dialog,
            text=f"✏️ Edit Product: {product['name']}",
            font=("Arial", 14, "bold")
        ).pack(pady=15)
        
        # Form frame
        form_frame = tk.Frame(dialog, padx=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Product Code (readonly)
        tk.Label(form_frame, text="Product Code:", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=8)
        code_label = tk.Label(form_frame, text=product['product_code'], font=("Arial", 11), fg="gray")
        code_label.grid(row=0, column=1, sticky="w", pady=8)
        
        # Product Name
        tk.Label(form_frame, text="Product Name:", font=("Arial", 11)).grid(row=1, column=0, sticky="w", pady=8)
        name_entry = tk.Entry(form_frame, font=("Arial", 11), width=25)
        name_entry.grid(row=1, column=1, pady=8, sticky="ew")
        name_entry.insert(0, product['name'])
        
        # Quality
        tk.Label(form_frame, text="Quality:", font=("Arial", 11)).grid(row=2, column=0, sticky="w", pady=8)
        quality_var = tk.StringVar(value=product['quality'])
        quality_frame = tk.Frame(form_frame)
        quality_frame.grid(row=2, column=1, sticky="w", pady=8)
        
        tk.Radiobutton(quality_frame, text="Premium", variable=quality_var, value="premium").pack(side=tk.LEFT)
        tk.Radiobutton(quality_frame, text="Standard", variable=quality_var, value="standard").pack(side=tk.LEFT)
        tk.Radiobutton(quality_frame, text="Economic", variable=quality_var, value="economic").pack(side=tk.LEFT)
        
        # Price per KG
        tk.Label(form_frame, text="Price per KG (₹):", font=("Arial", 11)).grid(row=3, column=0, sticky="w", pady=8)
        price_kg_entry = tk.Entry(form_frame, font=("Arial", 11), width=25)
        price_kg_entry.grid(row=3, column=1, pady=8, sticky="ew")
        price_kg_entry.insert(0, str(product['price_per_kg']))
        
        # Bag Size
        tk.Label(form_frame, text="Bag Size (kg):", font=("Arial", 11)).grid(row=4, column=0, sticky="w", pady=8)
        bag_size_entry = tk.Entry(form_frame, font=("Arial", 11), width=25)
        bag_size_entry.grid(row=4, column=1, pady=8, sticky="ew")
        if product['bag_size_kg']:
            bag_size_entry.insert(0, str(product['bag_size_kg']))
        
        # Price per Bag
        tk.Label(form_frame, text="Price per Bag (₹):", font=("Arial", 11)).grid(row=5, column=0, sticky="w", pady=8)
        price_bag_entry = tk.Entry(form_frame, font=("Arial", 11), width=25)
        price_bag_entry.grid(row=5, column=1, pady=8, sticky="ew")
        if product['price_per_bag']:
            price_bag_entry.insert(0, str(product['price_per_bag']))
        
        # Description
        tk.Label(form_frame, text="Description:", font=("Arial", 11)).grid(row=6, column=0, sticky="nw", pady=8)
        desc_text = tk.Text(form_frame, font=("Arial", 10), width=25, height=4)
        desc_text.grid(row=6, column=1, pady=8, sticky="ew")
        if product['description']:
            desc_text.insert("1.0", product['description'])
        
        # Active status
        tk.Label(form_frame, text="Status:", font=("Arial", 11)).grid(row=7, column=0, sticky="w", pady=8)
        active_var = tk.IntVar(value=product['is_active'])
        tk.Checkbutton(form_frame, text="Active", variable=active_var, font=("Arial", 11)).grid(row=7, column=1, sticky="w", pady=8)
        
        form_frame.columnconfigure(1, weight=1)
        
        def update_product():
            try:
                name = name_entry.get().strip()
                quality = quality_var.get()
                price_kg = float(price_kg_entry.get())
                
                if not name:
                    messagebox.showerror("Error", "Product name is required")
                    return
                
                if price_kg <= 0:
                    messagebox.showerror("Error", "Price per kg must be greater than 0")
                    return
                
                # Optional fields
                bag_size = None
                price_bag = None
                
                if bag_size_entry.get().strip():
                    bag_size = float(bag_size_entry.get())
                
                if price_bag_entry.get().strip():
                    price_bag = float(price_bag_entry.get())
                
                description = desc_text.get("1.0", tk.END).strip()
                
                # Update product in database
                success = db.update_product(
                    product_id=product['id'],
                    name=name,
                    quality=quality,
                    price_per_kg=price_kg,
                    bag_size_kg=bag_size,
                    price_per_bag=price_bag,
                    description=description or None,
                    is_active=active_var.get()
                )
                
                if success:
                    messagebox.showinfo("Success", "Product updated successfully!")
                    dialog.destroy()
                    self.load_products()
                else:
                    messagebox.showerror("Error", "Failed to update product")
            
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for prices")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {str(e)}")
        
        # Buttons
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame,
            text="Update Product",
            font=("Arial", 11, "bold"),
            bg="#3498db",
            fg="white",
            padx=30,
            pady=8,
            command=update_product
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            font=("Arial", 11),
            padx=30,
            pady=8,
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
        
        name_entry.focus()