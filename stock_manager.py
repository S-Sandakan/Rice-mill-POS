"""
Rice Mill POS System - Stock Management Module
Handles stock updates, restocking, and adjustments
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import db


class StockManagerWindow:
    """Stock Management Window"""
    
    def __init__(self, parent, user_data):
        self.window = tk.Toplevel(parent)
        self.window.title("Stock Management")
        self.window.geometry("900x600")
        self.user_data = user_data
        
        self.create_widgets()
        self.load_stock_data()
    
    def create_widgets(self):
        """Create stock management widgets"""
        # Header
        header = tk.Label(
            self.window,
            text="📦 Stock Management",
            font=("Arial", 16, "bold"),
            bg="#3498db",
            fg="white",
            pady=10
        )
        header.pack(fill=tk.X)
        
        # Main frame
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Stock list frame
        list_frame = tk.LabelFrame(main_frame, text="Current Stock", font=("Arial", 12, "bold"))
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create treeview
        columns = ('code', 'name', 'quality', 'kg', 'bags', 'min_kg', 'status')
        self.stock_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        self.stock_tree.heading('code', text='Product Code')
        self.stock_tree.heading('name', text='Product Name')
        self.stock_tree.heading('quality', text='Quality')
        self.stock_tree.heading('kg', text='Stock (kg)')
        self.stock_tree.heading('bags', text='Bags')
        self.stock_tree.heading('min_kg', text='Min Stock (kg)')
        self.stock_tree.heading('status', text='Status')
        
        self.stock_tree.column('code', width=100)
        self.stock_tree.column('name', width=180)
        self.stock_tree.column('quality', width=100)
        self.stock_tree.column('kg', width=100)
        self.stock_tree.column('bags', width=80)
        self.stock_tree.column('min_kg', width=100)
        self.stock_tree.column('status', width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.stock_tree.yview)
        self.stock_tree.configure(yscrollcommand=scrollbar.set)
        
        self.stock_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Color code rows
        self.stock_tree.tag_configure('low_stock', background='#ffcccc')
        self.stock_tree.tag_configure('out_of_stock', background='#ff9999')
        self.stock_tree.tag_configure('available', background='#ccffcc')
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        tk.Button(
            buttons_frame,
            text="➕ Restock",
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=8,
            command=self.restock_dialog
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            buttons_frame,
            text="🔧 Adjust Stock",
            font=("Arial", 11, "bold"),
            bg="#f39c12",
            fg="white",
            padx=20,
            pady=8,
            command=self.adjust_stock_dialog
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            buttons_frame,
            text="📊 Stock History",
            font=("Arial", 11, "bold"),
            bg="#3498db",
            fg="white",
            padx=20,
            pady=8,
            command=self.show_stock_history
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            buttons_frame,
            text="🔄 Refresh",
            font=("Arial", 11),
            bg="#95a5a6",
            fg="white",
            padx=20,
            pady=8,
            command=self.load_stock_data
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            buttons_frame,
            text="Close",
            font=("Arial", 11),
            padx=20,
            pady=8,
            command=self.window.destroy
        ).pack(side=tk.RIGHT, padx=5)
    
    def load_stock_data(self):
        """Load stock data into treeview"""
        # Clear existing data
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)
        
        # Load from database
        stock_data = db.get_all_stock_status()
        
        for item in stock_data:
            # Determine tag for color coding
            if item['stock_status'] == 'Out of Stock':
                tag = 'out_of_stock'
            elif item['stock_status'] == 'Low Stock':
                tag = 'low_stock'
            else:
                tag = 'available'
            
            self.stock_tree.insert('', tk.END, values=(
                item['product_code'],
                item['name'],
                item['quality'],
                f"{item['quantity_kg']:.2f}",
                item['quantity_bags'],
                f"{item['min_stock_kg']:.2f}",
                item['stock_status']
            ), tags=(tag,))
    
    def restock_dialog(self):
        """Show restock dialog"""
        selection = self.stock_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to restock")
            return
        
        # Get selected product data
        item_values = self.stock_tree.item(selection[0])['values']
        product_code = item_values[0]
        product_name = item_values[1]
        
        # Get product from database
        product = db.fetch_one("SELECT * FROM products WHERE product_code = ?", (product_code,))
        
        # Create dialog
        dialog = tk.Toplevel(self.window)
        dialog.title("Restock Product")
        dialog.geometry("400x300")
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Product info
        tk.Label(
            dialog,
            text=f"Restocking: {product_name}",
            font=("Arial", 13, "bold")
        ).pack(pady=15)
        
        # Input frame
        input_frame = tk.Frame(dialog)
        input_frame.pack(pady=10)
        
        # Quantity in KG
        tk.Label(input_frame, text="Quantity (kg):", font=("Arial", 11)).grid(row=0, column=0, sticky="w", padx=10, pady=10)
        kg_entry = tk.Entry(input_frame, font=("Arial", 11), width=15)
        kg_entry.grid(row=0, column=1, padx=10, pady=10)
        kg_entry.insert(0, "0")
        
        # Quantity in Bags
        tk.Label(input_frame, text="Number of Bags:", font=("Arial", 11)).grid(row=1, column=0, sticky="w", padx=10, pady=10)
        bags_entry = tk.Entry(input_frame, font=("Arial", 11), width=15)
        bags_entry.grid(row=1, column=1, padx=10, pady=10)
        bags_entry.insert(0, "0")
        
        # Notes
        tk.Label(input_frame, text="Notes:", font=("Arial", 11)).grid(row=2, column=0, sticky="w", padx=10, pady=10)
        notes_entry = tk.Entry(input_frame, font=("Arial", 11), width=15)
        notes_entry.grid(row=2, column=1, padx=10, pady=10)
        
        def perform_restock():
            try:
                kg = float(kg_entry.get())
                bags = int(bags_entry.get())
                notes = notes_entry.get()
                
                if kg <= 0 and bags <= 0:
                    messagebox.showerror("Error", "Please enter quantity to restock")
                    return
                
                # Update stock
                success = db.update_stock(
                    product_id=product['id'],
                    quantity_kg_change=kg,
                    quantity_bags_change=bags,
                    user_id=self.user_data['id'],
                    transaction_type='restock',
                    notes=notes or "Stock restocked"
                )
                
                if success:
                    messagebox.showinfo("Success", "Stock updated successfully!")
                    dialog.destroy()
                    self.load_stock_data()
                else:
                    messagebox.showerror("Error", "Failed to update stock")
            
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers")
        
        # Buttons
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame,
            text="Restock",
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=5,
            command=perform_restock
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            font=("Arial", 11),
            padx=20,
            pady=5,
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
        
        kg_entry.focus()
    
    def adjust_stock_dialog(self):
        """Show stock adjustment dialog"""
        selection = self.stock_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to adjust")
            return
        
        # Get selected product data
        item_values = self.stock_tree.item(selection[0])['values']
        product_code = item_values[0]
        product_name = item_values[1]
        current_kg = float(item_values[3])
        current_bags = int(item_values[4])
        
        # Get product from database
        product = db.fetch_one("SELECT * FROM products WHERE product_code = ?", (product_code,))
        
        # Create dialog
        dialog = tk.Toplevel(self.window)
        dialog.title("Adjust Stock")
        dialog.geometry("450x350")
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Product info
        tk.Label(
            dialog,
            text=f"Adjusting: {product_name}",
            font=("Arial", 13, "bold")
        ).pack(pady=15)
        
        tk.Label(
            dialog,
            text=f"Current Stock: {current_kg:.2f}kg, {current_bags} bags",
            font=("Arial", 10),
            fg="gray"
        ).pack()
        
        # Input frame
        input_frame = tk.Frame(dialog)
        input_frame.pack(pady=10)
        
        # Adjustment type
        tk.Label(input_frame, text="Adjustment Type:", font=("Arial", 11)).grid(row=0, column=0, sticky="w", padx=10, pady=10)
        adj_type = tk.StringVar(value="add")
        
        type_frame = tk.Frame(input_frame)
        type_frame.grid(row=0, column=1, sticky="w", padx=10, pady=10)
        tk.Radiobutton(type_frame, text="Add", variable=adj_type, value="add").pack(side=tk.LEFT)
        tk.Radiobutton(type_frame, text="Subtract", variable=adj_type, value="subtract").pack(side=tk.LEFT)
        
        # Quantity in KG
        tk.Label(input_frame, text="Adjust KG:", font=("Arial", 11)).grid(row=1, column=0, sticky="w", padx=10, pady=10)
        kg_entry = tk.Entry(input_frame, font=("Arial", 11), width=15)
        kg_entry.grid(row=1, column=1, padx=10, pady=10)
        kg_entry.insert(0, "0")
        
        # Quantity in Bags
        tk.Label(input_frame, text="Adjust Bags:", font=("Arial", 11)).grid(row=2, column=0, sticky="w", padx=10, pady=10)
        bags_entry = tk.Entry(input_frame, font=("Arial", 11), width=15)
        bags_entry.grid(row=2, column=1, padx=10, pady=10)
        bags_entry.insert(0, "0")
        
        # Reason (required for adjustments)
        tk.Label(input_frame, text="Reason (Required):", font=("Arial", 11)).grid(row=3, column=0, sticky="w", padx=10, pady=10)
        reason_entry = tk.Entry(input_frame, font=("Arial", 11), width=15)
        reason_entry.grid(row=3, column=1, padx=10, pady=10)
        
        def perform_adjustment():
            try:
                kg = float(kg_entry.get())
                bags = int(bags_entry.get())
                reason = reason_entry.get().strip()
                
                if not reason:
                    messagebox.showerror("Error", "Please enter a reason for adjustment")
                    return
                
                if kg <= 0 and bags <= 0:
                    messagebox.showerror("Error", "Please enter quantity to adjust")
                    return
                
                # Apply negative if subtracting
                if adj_type.get() == "subtract":
                    kg = -kg
                    bags = -bags
                
                # Check if subtraction would result in negative stock
                if current_kg + kg < 0 or current_bags + bags < 0:
                    messagebox.showerror("Error", "Adjustment would result in negative stock")
                    return
                
                # Update stock
                success = db.update_stock(
                    product_id=product['id'],
                    quantity_kg_change=kg,
                    quantity_bags_change=bags,
                    user_id=self.user_data['id'],
                    transaction_type='adjustment',
                    notes=f"Adjustment: {reason}"
                )
                
                if success:
                    messagebox.showinfo("Success", "Stock adjusted successfully!")
                    dialog.destroy()
                    self.load_stock_data()
                else:
                    messagebox.showerror("Error", "Failed to adjust stock")
            
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers")
        
        # Buttons
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame,
            text="Apply Adjustment",
            font=("Arial", 11, "bold"),
            bg="#f39c12",
            fg="white",
            padx=20,
            pady=5,
            command=perform_adjustment
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            font=("Arial", 11),
            padx=20,
            pady=5,
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
        
        kg_entry.focus()
    
    def show_stock_history(self):
        """Show stock transaction history"""
        selection = self.stock_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to view history")
            return
        
        # Get selected product data
        item_values = self.stock_tree.item(selection[0])['values']
        product_code = item_values[0]
        product_name = item_values[1]
        
        # Get product from database
        product = db.fetch_one("SELECT * FROM products WHERE product_code = ?", (product_code,))
        
        # Get transaction history
        transactions = db.fetch_all(
            """SELECT st.*, u.full_name as performed_by_name
               FROM stock_transactions st
               JOIN users u ON st.performed_by = u.id
               WHERE st.product_id = ?
               ORDER BY st.transaction_date DESC
               LIMIT 50""",
            (product['id'],)
        )
        
        # Create history window
        history_window = tk.Toplevel(self.window)
        history_window.title(f"Stock History - {product_name}")
        history_window.geometry("900x500")
        
        tk.Label(
            history_window,
            text=f"Stock History: {product_name}",
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        # Create treeview
        columns = ('date', 'type', 'kg_change', 'bags_change', 'user', 'notes')
        history_tree = ttk.Treeview(history_window, columns=columns, show='headings', height=20)
        
        history_tree.heading('date', text='Date/Time')
        history_tree.heading('type', text='Type')
        history_tree.heading('kg_change', text='KG Change')
        history_tree.heading('bags_change', text='Bags Change')
        history_tree.heading('user', text='Performed By')
        history_tree.heading('notes', text='Notes')
        
        history_tree.column('date', width=150)
        history_tree.column('type', width=100)
        history_tree.column('kg_change', width=100)
        history_tree.column('bags_change', width=100)
        history_tree.column('user', width=120)
        history_tree.column('notes', width=300)
        
        # Load data
        for trans in transactions:
            kg_change = trans['quantity_kg_change'] or 0
            bags_change = trans['quantity_bags_change'] or 0
            
            history_tree.insert('', tk.END, values=(
                trans['transaction_date'],
                trans['transaction_type'].title(),
                f"{kg_change:+.2f}",
                f"{bags_change:+d}",
                trans['performed_by_name'],
                trans['notes'] or ''
            ))
        
        history_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Button(
            history_window,
            text="Close",
            font=("Arial", 11),
            command=history_window.destroy
        ).pack(pady=10)