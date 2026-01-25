"""
Rice Mill POS System - Main Application
Complete offline POS system with Tkinter GUI
Version: 1.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from typing import Optional, Dict, List
import sys
import os

# Import database module
try:
    from database import db
except ImportError:
    print("ERROR: database.py not found!")
    print("Please ensure database.py is in the same directory as main.py")
    sys.exit(1)

# Import additional modules (optional)
try:
    from stock_manager import StockManagerWindow
    STOCK_MANAGER_AVAILABLE = True
except ImportError:
    STOCK_MANAGER_AVAILABLE = False
    print("Note: stock_manager.py not found. Stock management features will be limited.")

try:
    from product_manager import ProductManagerWindow
    PRODUCT_MANAGER_AVAILABLE = True
except ImportError:
    PRODUCT_MANAGER_AVAILABLE = False
    print("Note: product_manager.py not found. Product management features will be limited.")

try:
    from reports import ReportsWindow
    REPORTS_AVAILABLE = True
except ImportError:
    REPORTS_AVAILABLE = False
    print("Note: reports.py not found. Advanced reporting features will be limited.")


class LoginWindow:
    """Login window for user authentication"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Rice Mill POS - Login")
        self.root.geometry("450x350")
        self.root.resizable(False, False)
        
        self.user_data = None
        self.create_widgets()
        self.center_window()
        
        # Set window icon if available
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create login form widgets"""
        # Main frame with background
        main_frame = tk.Frame(self.root, bg="#ecf0f1")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with icon
        header_frame = tk.Frame(main_frame, bg="#2c3e50", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        header = tk.Label(
            header_frame, 
            text="🌾 Rice Mill POS", 
            font=("Arial", 24, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        header.pack(pady=20)
        
        # Login form frame
        form_frame = tk.Frame(main_frame, bg="#ecf0f1", padx=50, pady=30)
        form_frame.pack(expand=True)
        
        # Username field
        tk.Label(
            form_frame, 
            text="Username:", 
            font=("Arial", 12),
            bg="#ecf0f1"
        ).grid(row=0, column=0, sticky="w", pady=15)
        
        self.username_entry = tk.Entry(
            form_frame, 
            font=("Arial", 12), 
            width=25,
            relief=tk.SOLID,
            borderwidth=1
        )
        self.username_entry.grid(row=0, column=1, pady=15, padx=10)
        self.username_entry.focus()
        
        # Password field
        tk.Label(
            form_frame, 
            text="Password:", 
            font=("Arial", 12),
            bg="#ecf0f1"
        ).grid(row=1, column=0, sticky="w", pady=15)
        
        self.password_entry = tk.Entry(
            form_frame, 
            font=("Arial", 12), 
            width=25, 
            show="●",
            relief=tk.SOLID,
            borderwidth=1
        )
        self.password_entry.grid(row=1, column=1, pady=15, padx=10)
        
        # Login button
        login_btn = tk.Button(
            form_frame, 
            text="LOGIN", 
            font=("Arial", 13, "bold"),
            bg="#27ae60",
            fg="white",
            padx=40,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.login
        )
        login_btn.grid(row=2, column=0, columnspan=2, pady=25)
        
        # Bind Enter key
        self.root.bind('<Return>', lambda e: self.login())
        
        # Footer with info
        footer_frame = tk.Frame(main_frame, bg="#ecf0f1")
        footer_frame.pack(side=tk.BOTTOM, pady=15)
        
        tk.Label(
            footer_frame,
            text="Default Login:",
            font=("Arial", 9, "bold"),
            bg="#ecf0f1",
            fg="#7f8c8d"
        ).pack()
        
        tk.Label(
            footer_frame,
            text="Username: admin | Password: admin123",
            font=("Arial", 9),
            bg="#ecf0f1",
            fg="#95a5a6"
        ).pack()
    
    def login(self):
        """Handle login attempt"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror(
                "Login Error", 
                "Please enter both username and password",
                parent=self.root
            )
            return
        
        user = db.authenticate_user(username, password)
        
        if user:
            self.user_data = user
            self.root.destroy()
        else:
            messagebox.showerror(
                "Login Failed", 
                "Invalid username or password.\nPlease try again.",
                parent=self.root
            )
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()


class POSApplication:
    """Main POS Application"""
    
    def __init__(self, root, user_data):
        self.root = root
        self.user_data = user_data
        self.root.title(f"Rice Mill POS - {user_data['full_name']} ({user_data['role'].title()})")
        
        # Set window size and make it maximizable
        self.root.geometry("1280x720")
        self.root.state('zoomed') if os.name == 'nt' else self.root.attributes('-zoomed', True)
        
        # Sale cart
        self.cart_items = []
        self.discount_amount = 0
        self.discount_reason = ""
        self.products = []
        
        # Create GUI
        self.create_menu()
        self.create_widgets()
        self.load_products()
        self.update_today_summary()
        
        # Auto-refresh summary every minute
        self.schedule_refresh()
        
        # Set window icon if available
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def schedule_refresh(self):
        """Schedule periodic refresh of summary"""
        self.update_today_summary()
        self.root.after(60000, self.schedule_refresh)  # Refresh every minute
    
    def create_menu(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(
            label="New Sale", 
            command=self.clear_cart, 
            accelerator="F1"
        )
        file_menu.add_separator()
        file_menu.add_command(label="Backup Database", command=self.backup_database)
        file_menu.add_separator()
        file_menu.add_command(label="Logout", command=self.logout)
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Products menu (Admin only)
        if self.user_data['role'] == 'admin':
            products_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Products", menu=products_menu)
            products_menu.add_command(
                label="Manage Products", 
                command=self.manage_products
            )
            products_menu.add_command(
                label="Manage Stock", 
                command=self.manage_stock_dialog
            )
            products_menu.add_separator()
            products_menu.add_command(
                label="Add New Product", 
                command=self.add_product_quick
            )
        
        # Reports menu
        reports_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Reports", menu=reports_menu)
        reports_menu.add_command(
            label="Sales Reports", 
            command=self.show_reports
        )
        reports_menu.add_command(
            label="Stock Status", 
            command=self.show_stock_status
        )
        reports_menu.add_separator()
        reports_menu.add_command(
            label="Today's Summary", 
            command=self.show_today_detailed_summary
        )
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(
            label="Database Info", 
            command=self.show_database_info
        )
        tools_menu.add_command(
            label="Export Data", 
            command=self.export_data_dialog
        )
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
        
        # Bind keyboard shortcuts
        self.root.bind('<F1>', lambda e: self.clear_cart())
        self.root.bind('<F2>', lambda e: self.add_to_cart())
        self.root.bind('<F5>', lambda e: self.load_products())
        self.root.bind('<Escape>', lambda e: self.clear_cart())
    
    def create_widgets(self):
        """Create main application widgets"""
        # Top frame - Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Left side - Title
        title_frame = tk.Frame(header_frame, bg="#2c3e50")
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        tk.Label(
            title_frame,
            text="🌾 Rice Mill POS",
            font=("Arial", 20, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack(side=tk.LEFT, padx=25, pady=15)
        
        # Right side - User info and status
        info_frame = tk.Frame(header_frame, bg="#2c3e50")
        info_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=20)
        
        tk.Label(
            info_frame,
            text=f"👤 {self.user_data['full_name']}",
            font=("Arial", 11),
            bg="#2c3e50",
            fg="#ecf0f1"
        ).pack(side=tk.TOP, pady=(15, 0))
        
        tk.Label(
            info_frame,
            text=f"Role: {self.user_data['role'].upper()}",
            font=("Arial", 9),
            bg="#2c3e50",
            fg="#95a5a6"
        ).pack(side=tk.TOP)
        
        self.status_label = tk.Label(
            info_frame,
            text="● OFFLINE MODE",
            font=("Arial", 10, "bold"),
            bg="#2c3e50",
            fg="#e74c3c"
        )
        self.status_label.pack(side=tk.TOP, pady=(5, 0))
        
        # Main container
        main_container = tk.Frame(self.root, bg="#ecf0f1")
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Products
        left_panel = tk.LabelFrame(
            main_container,
            text="  📦 Available Products  ",
            font=("Arial", 13, "bold"),
            bg="white",
            fg="#2c3e50"
        )
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Search box
        search_frame = tk.Frame(left_panel, bg="white")
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            search_frame,
            text="🔍",
            font=("Arial", 12),
            bg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_products)
        
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Arial", 11),
            relief=tk.SOLID,
            borderwidth=1
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Products list with scrollbar
        products_frame = tk.Frame(left_panel, bg="white")
        products_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(products_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.products_listbox = tk.Listbox(
            products_frame,
            font=("Arial", 11),
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE,
            activestyle='dotbox',
            relief=tk.FLAT,
            borderwidth=0
        )
        self.products_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.products_listbox.yview)
        
        # Bind double-click
        self.products_listbox.bind('<Double-1>', lambda e: self.add_to_cart())
        
        # Add to cart button
        btn_frame = tk.Frame(left_panel, bg="white")
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        add_btn = tk.Button(
            btn_frame,
            text="➕ Add to Cart (F2)",
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=12,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.add_to_cart
        )
        add_btn.pack(fill=tk.X)
        
        tk.Button(
            btn_frame,
            text="🔄 Refresh (F5)",
            font=("Arial", 10),
            bg="#95a5a6",
            fg="white",
            padx=15,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.load_products
        ).pack(fill=tk.X, pady=(5, 0))
        
        # Right panel - Cart and Checkout
        right_panel = tk.LabelFrame(
            main_container,
            text="  🛒 Shopping Cart  ",
            font=("Arial", 13, "bold"),
            bg="white",
            fg="#2c3e50"
        )
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Cart treeview with scrollbar
        cart_frame = tk.Frame(right_panel, bg="white")
        cart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create style for treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Cart.Treeview",
            background="white",
            foreground="black",
            rowheight=30,
            fieldbackground="white",
            font=("Arial", 10)
        )
        style.configure(
            "Cart.Treeview.Heading",
            font=("Arial", 11, "bold"),
            background="#34495e",
            foreground="white"
        )
        style.map('Cart.Treeview', background=[('selected', '#3498db')])
        
        columns = ('product', 'type', 'quantity', 'price', 'subtotal')
        self.cart_tree = ttk.Treeview(
            cart_frame,
            columns=columns,
            show='headings',
            height=12,
            style="Cart.Treeview"
        )
        
        self.cart_tree.heading('product', text='Product')
        self.cart_tree.heading('type', text='Type')
        self.cart_tree.heading('quantity', text='Quantity')
        self.cart_tree.heading('price', text='Price')
        self.cart_tree.heading('subtotal', text='Subtotal')
        
        self.cart_tree.column('product', width=220)
        self.cart_tree.column('type', width=90)
        self.cart_tree.column('quantity', width=100)
        self.cart_tree.column('price', width=100)
        self.cart_tree.column('subtotal', width=100)
        
        cart_scrollbar = tk.Scrollbar(cart_frame, command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=cart_scrollbar.set)
        
        self.cart_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cart_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to edit cart item
        self.cart_tree.bind('<Double-1>', lambda e: self.edit_cart_item())
        
        # Cart action buttons
        cart_btn_frame = tk.Frame(right_panel, bg="white")
        cart_btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Button(
            cart_btn_frame,
            text="✏️ Edit Selected",
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            padx=15,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.edit_cart_item
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            cart_btn_frame,
            text="❌ Remove Selected",
            font=("Arial", 10),
            bg="#e74c3c",
            fg="white",
            padx=15,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.remove_from_cart
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            cart_btn_frame,
            text="🗑️ Clear Cart (ESC)",
            font=("Arial", 10),
            bg="#95a5a6",
            fg="white",
            padx=15,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.clear_cart
        ).pack(side=tk.LEFT, padx=2)
        
        # Total frame
        total_frame = tk.Frame(right_panel, bg="#ecf0f1", relief=tk.RIDGE, borderwidth=2)
        total_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.subtotal_label = tk.Label(
            total_frame,
            text="Subtotal: ₹0.00",
            font=("Arial", 13),
            bg="#ecf0f1",
            anchor="e"
        )
        self.subtotal_label.pack(fill=tk.X, padx=15, pady=(10, 5))
        
        self.discount_label = tk.Label(
            total_frame,
            text="Discount: ₹0.00",
            font=("Arial", 13),
            bg="#ecf0f1",
            fg="#e74c3c",
            anchor="e"
        )
        self.discount_label.pack(fill=tk.X, padx=15, pady=5)
        
        separator = tk.Frame(total_frame, height=2, bg="#95a5a6")
        separator.pack(fill=tk.X, padx=15, pady=5)
        
        self.total_label = tk.Label(
            total_frame,
            text="TOTAL: ₹0.00",
            font=("Arial", 18, "bold"),
            bg="#ecf0f1",
            fg="#27ae60",
            anchor="e"
        )
        self.total_label.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        # Checkout buttons
        checkout_frame = tk.Frame(right_panel, bg="white")
        checkout_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        if self.user_data['role'] == 'admin':
            tk.Button(
                checkout_frame,
                text="💰 Apply Discount",
                font=("Arial", 11),
                bg="#f39c12",
                fg="white",
                padx=20,
                pady=10,
                relief=tk.FLAT,
                cursor="hand2",
                command=self.apply_discount
            ).pack(fill=tk.X, pady=(0, 5))
        
        buttons_inner_frame = tk.Frame(checkout_frame, bg="white")
        buttons_inner_frame.pack(fill=tk.X)
        
        tk.Button(
            buttons_inner_frame,
            text="💵 CASH SALE",
            font=("Arial", 13, "bold"),
            bg="#27ae60",
            fg="white",
            padx=25,
            pady=15,
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self.checkout('cash')
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        
        tk.Button(
            buttons_inner_frame,
            text="📄 CREDIT SALE",
            font=("Arial", 13, "bold"),
            bg="#3498db",
            fg="white",
            padx=25,
            pady=15,
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self.checkout('credit')
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(3, 0))
        
        # Bottom panel - Today's summary
        bottom_panel = tk.Frame(self.root, bg="white", relief=tk.RIDGE, borderwidth=1)
        bottom_panel.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(0, 10))
        
        tk.Label(
            bottom_panel,
            text="📊 TODAY'S SUMMARY",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(pady=(10, 5))
        
        summary_frame = tk.Frame(bottom_panel, bg="white")
        summary_frame.pack(pady=(0, 10))
        
        # Summary cards
        self.create_summary_card(
            summary_frame,
            "💰 Total Sales",
            "₹0.00",
            "#27ae60",
            "summary_sales"
        )
        
        self.create_summary_card(
            summary_frame,
            "📝 Transactions",
            "0",
            "#3498db",
            "summary_trans"
        )
        
        self.create_summary_card(
            summary_frame,
            "💵 Cash",
            "₹0.00",
            "#f39c12",
            "summary_cash"
        )
        
        self.create_summary_card(
            summary_frame,
            "📄 Credit",
            "₹0.00",
            "#e74c3c",
            "summary_credit"
        )
    
    def create_summary_card(self, parent, title, value, color, var_name):
        """Create a summary card widget"""
        card = tk.Frame(parent, bg=color, relief=tk.RAISED, borderwidth=1)
        card.pack(side=tk.LEFT, padx=8, ipadx=20, ipady=10)
        
        tk.Label(
            card,
            text=title,
            font=("Arial", 10),
            bg=color,
            fg="white"
        ).pack()
        
        label = tk.Label(
            card,
            text=value,
            font=("Arial", 16, "bold"),
            bg=color,
            fg="white"
        )
        label.pack(pady=(5, 0))
        
        # Store reference to label
        setattr(self, f"{var_name}_label", label)
    
    def filter_products(self, *args):
        """Filter products based on search term"""
        search_term = self.search_var.get().lower()
        
        self.products_listbox.delete(0, tk.END)
        
        for product in self.products:
            product_text = f"{product['name']} {product['quality']} {product['product_code']}".lower()
            
            if search_term in product_text:
                stock = db.get_stock_by_product(product['id'])
                stock_info = f" ({stock['quantity_kg']:.1f}kg, {stock['quantity_bags']} bags)" if stock else ""
                
                display = f"{product['name']} - ₹{product['price_per_kg']:.2f}/kg{stock_info}"
                self.products_listbox.insert(tk.END, display)
    
    def load_products(self):
        """Load products into listbox"""
        self.products_listbox.delete(0, tk.END)
        self.products = db.get_all_products()
        
        for product in self.products:
            stock = db.get_stock_by_product(product['id'])
            stock_info = f" ({stock['quantity_kg']:.1f}kg, {stock['quantity_bags']} bags)" if stock else ""
            
            display = f"{product['name']} - ₹{product['price_per_kg']:.2f}/kg{stock_info}"
            self.products_listbox.insert(tk.END, display)
        
        # Clear search
        self.search_var.set("")
    
    def add_to_cart(self):
        """Add selected product to cart"""
        selection = self.products_listbox.curselection()
        if not selection:
            messagebox.showwarning(
                "No Selection",
                "Please select a product from the list",
                parent=self.root
            )
            return
        
        # Find the actual product based on the displayed text
        selected_index = selection[0]
        displayed_items = list(self.products_listbox.get(0, tk.END))
        selected_text = displayed_items[selected_index]
        
        # Match with actual products
        product = None
        for p in self.products:
            stock = db.get_stock_by_product(p['id'])
            stock_info = f" ({stock['quantity_kg']:.1f}kg, {stock['quantity_bags']} bags)" if stock else ""
            expected_text = f"{p['name']} - ₹{p['price_per_kg']:.2f}/kg{stock_info}"
            
            if expected_text == selected_text:
                product = p
                break
        
        if not product:
            messagebox.showerror("Error", "Product not found", parent=self.root)
            return
        
        # Dialog to choose sale type and quantity
        dialog = tk.Toplevel(self.root)
        dialog.title("Add to Cart")
        dialog.geometry("400x280")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Header
        header = tk.Frame(dialog, bg="#3498db")
        header.pack(fill=tk.X)
        
        tk.Label(
            header,
            text=f"📦 {product['name']}",
            font=("Arial", 14, "bold"),
            bg="#3498db",
            fg="white"
        ).pack(pady=15)
        
        # Form
        form_frame = tk.Frame(dialog, padx=30, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sale type
        tk.Label(
            form_frame,
            text="Sale Type:",
            font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        sale_type_var = tk.StringVar(value="by_kg")
        
        type_frame = tk.Frame(form_frame)
        type_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Radiobutton(
            type_frame,
            text=f"By Kilogram - ₹{product['price_per_kg']:.2f}/kg",
            variable=sale_type_var,
            value="by_kg",
            font=("Arial", 10)
        ).pack(anchor=tk.W, pady=2)
        
        if product.get('bag_size_kg') and product.get('price_per_bag'):
            tk.Radiobutton(
                type_frame,
                text=f"By Bag ({product['bag_size_kg']}kg) - ₹{product['price_per_bag']:.2f}/bag",
                variable=sale_type_var,
                value="by_bag",
                font=("Arial", 10)
            ).pack(anchor=tk.W, pady=2)
        
        # Quantity
        tk.Label(
            form_frame,
            text="Quantity:",
            font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        quantity_var = tk.StringVar(value="1")
        quantity_entry = tk.Entry(
            form_frame,
            textvariable=quantity_var,
            font=("Arial", 11),
            width=10,
            relief=tk.SOLID,
            borderwidth=1
        )
        quantity_entry.pack(anchor="w")
        quantity_entry.focus()

        # Buttons
        btn_frame = tk.Frame(dialog)    
        btn_frame.pack(pady=15)

        tk.Button(
            btn_frame,
            text="Add to Cart",
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self.confirm_add_to_cart(
                dialog,
                product,
                sale_type_var.get(),
                quantity_var.get()
            )
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            font=("Arial", 11),
            bg="#e74c3c",
            fg="white",
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=10)
    
    def confirm_add_to_cart(self, dialog, product, sale_type, quantity_str):
        """Confirm adding product to cart"""
        try:
            quantity = float(quantity_str)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid Quantity",
                "Please enter a valid positive number for quantity",
                parent=dialog
            )
            return
        
        # Check stock availability
        stock = db.get_stock_by_product(product['id'])
        if not stock:
            messagebox.showerror(
                "Out of Stock",
                "This product is currently out of stock",
                parent=dialog
            )
            return
        
        if sale_type == 'by_kg':
            if quantity > stock['quantity_kg']:
                messagebox.showerror(
                    "Insufficient Stock",
                    f"Only {stock['quantity_kg']:.1f} kg available in stock",
                    parent=dialog
                )
                return
            price = product['price_per_kg']
            qty_display = f"{quantity:.2f} kg"
        else:
            quantity = int(quantity)
            if quantity > stock['quantity_bags']:
                messagebox.showerror(
                    "Insufficient Stock",
                    f"Only {stock['quantity_bags']} bags available in stock",
                    parent=dialog
                )
                return
            price = product['price_per_bag']
            qty_display = f"{quantity} bags"

        subtotal = price * quantity
        cart_item = {
            'product_id': product['id'],
            'product_name': product['name'],
            'sale_type': sale_type,
            'quantity': quantity,
            'price': price,
            'subtotal': subtotal
        }
        
        self.cart_items.append(cart_item)
        self.refresh_cart()
        dialog.destroy()
    
    def refresh_cart(self):
        """Refresh cart display"""
        self.cart_tree.delete(*self.cart_tree.get_children())
        
        for item in self.cart_items:
            if item['sale_type'] == 'by_kg':
                qty_display = f"{item['quantity']:.2f} kg"
            else:
                qty_display = f"{item['quantity']} bags"
            
            self.cart_tree.insert('', tk.END, values=(
                item['product_name'],
                item['sale_type'].replace('_', ' ').title(),
                qty_display,
                f"₹{item['price']:.2f}",
                f"₹{item['subtotal']:.2f}"
            ))
        
        self.update_totals()
    
    def remove_from_cart(self):
        """Remove selected item from cart"""
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showwarning(
                "No Selection",
                "Please select an item from the cart to remove",
                parent=self.root
            )
            return
        
        # Get index
        index = self.cart_tree.index(selection[0])
        
        # Remove from cart
        del self.cart_items[index]
        
        # Remove from tree
        self.cart_tree.delete(selection[0])
        
        self.update_totals()
    
    def update_totals(self):
        """Update cart totals"""
        subtotal = sum(item['subtotal'] for item in self.cart_items)
        
        self.subtotal_label.config(text=f"Subtotal: ₹{subtotal:.2f}")
        self.discount_label.config(text=f"Discount: -₹{self.discount_amount:.2f}")
        
        total = subtotal - self.discount_amount
        self.total_label.config(text=f"TOTAL: ₹{total:.2f}")
    
    def edit_cart_item(self):
        """Edit selected item in cart"""
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showwarning(
                "No Selection",
                "Please select an item from the cart to edit",
                parent=self.root
            )
            return
        
        # Get the selected item index
        index = self.cart_tree.index(selection[0])
        item = self.cart_items[index]
        
        # Create edit dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Cart Item")
        dialog.geometry("400x280")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Header
        header = tk.Frame(dialog, bg="#f39c12")
        header.pack(fill=tk.X)
        
        tk.Label(
            header,
            text=f"✏️ {item['product_name']}",
            font=("Arial", 14, "bold"),
            bg="#f39c12",
            fg="white"
        ).pack(pady=15)
        
        # Form
        form_frame = tk.Frame(dialog, padx=30, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Quantity
        tk.Label(
            form_frame,
            text="Quantity:",
            font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        quantity_var = tk.StringVar(value=str(item['quantity']))
        quantity_entry = tk.Entry(
            form_frame,
            textvariable=quantity_var,
            font=("Arial", 11),
            width=10,
            relief=tk.SOLID,
            borderwidth=1
        )
        quantity_entry.pack(anchor="w", pady=(0, 20))
        quantity_entry.focus()
        quantity_entry.select_range(0, tk.END)
        
        # Price info
        tk.Label(
            form_frame,
            text=f"Price: ₹{item['price']:.2f}",
            font=("Arial", 10)
        ).pack(anchor="w", pady=(0, 10))
        
        # Buttons
        btn_frame = tk.Frame(dialog)    
        btn_frame.pack(pady=15)
        
        tk.Button(
            btn_frame,
            text="Update",
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self.confirm_edit_cart_item(dialog, index, quantity_var.get())
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            font=("Arial", 11),
            bg="#e74c3c",
            fg="white",
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=10)
    
    def confirm_edit_cart_item(self, dialog, index, quantity_str):
        """Confirm editing cart item"""
        try:
            quantity = float(quantity_str)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid Quantity",
                "Please enter a valid positive number",
                parent=dialog
            )
            return
        
        # Update item
        item = self.cart_items[index]
        
        # Check stock
        stock = db.get_stock_by_product(item['product_id'])
        if item['sale_type'] == 'by_kg':
            if quantity > stock['quantity_kg']:
                messagebox.showerror(
                    "Insufficient Stock",
                    f"Only {stock['quantity_kg']:.1f} kg available in stock",
                    parent=dialog
                )
                return
        else:
            quantity = int(quantity)
            if quantity > stock['quantity_bags']:
                messagebox.showerror(
                    "Insufficient Stock",
                    f"Only {stock['quantity_bags']} bags available in stock",
                    parent=dialog
                )
                return
        
        # Update cart item
        item['quantity'] = quantity
        item['subtotal'] = quantity * item['price']
        
        self.refresh_cart()
        dialog.destroy()
        
        messagebox.showinfo(
            "Item Updated",
            "Cart item updated successfully",
            parent=self.root
        )
    
    def apply_discount(self):
        """Apply discount to cart"""
        if not self.cart_items:
            messagebox.showwarning("Empty Cart", "Cannot apply discount to empty cart", parent=self.root)
            return
        
        subtotal = sum(item['subtotal'] for item in self.cart_items)
        
        discount = simpledialog.askfloat(
            "Apply Discount",
            f"Enter discount amount:\n\nSubtotal: ₹{subtotal:.2f}\nMax discount: ₹{subtotal:.2f}",
            minvalue=0,
            maxvalue=subtotal,
            parent=self.root
        )
        
        if discount is not None and discount > 0:
            reason = simpledialog.askstring(
                "Discount Reason",
                "Enter reason for discount:",
                parent=self.root
            )
            
            if reason and reason.strip():
                self.discount_amount = discount
                self.discount_reason = reason.strip()
                self.update_totals()
                messagebox.showinfo(
                    "Discount Applied",
                    f"Discount of ₹{discount:.2f} applied successfully",
                    parent=self.root
                )
            else:
                messagebox.showwarning(
                    "Reason Required",
                    "Discount reason is required",
                    parent=self.root
                )
    
    def checkout(self, payment_method):
        """Process checkout"""
        if not self.cart_items:
            messagebox.showwarning("Empty Cart", "Cannot checkout with empty cart", parent=self.root)
            return
        
        customer_name = None
        customer_phone = None
        
        if payment_method == 'credit':
            # Create customer info dialog
            customer_dialog = tk.Toplevel(self.root)
            customer_dialog.title("Credit Sale - Customer Information")
            customer_dialog.geometry("400x250")
            customer_dialog.transient(self.root)
            customer_dialog.grab_set()
            customer_dialog.resizable(False, False)
            
            # Center dialog
            customer_dialog.update_idletasks()
            x = (customer_dialog.winfo_screenwidth() // 2) - (customer_dialog.winfo_width() // 2)
            y = (customer_dialog.winfo_screenheight() // 2) - (customer_dialog.winfo_height() // 2)
            customer_dialog.geometry(f"+{x}+{y}")
            
            # Header
            header = tk.Frame(customer_dialog, bg="#e74c3c")
            header.pack(fill=tk.X)
            tk.Label(
                header,
                text="📄 Credit Sale",
                font=("Arial", 14, "bold"),
                bg="#e74c3c",
                fg="white"
            ).pack(pady=15)
            
            # Form
            form_frame = tk.Frame(customer_dialog, padx=30, pady=20)
            form_frame.pack(fill=tk.BOTH, expand=True)
            
            tk.Label(
                form_frame,
                text="Customer Name: *",
                font=("Arial", 11)
            ).pack(anchor="w", pady=(0, 5))
            
            name_entry = tk.Entry(
                form_frame,
                font=("Arial", 11),
                width=30,
                relief=tk.SOLID,
                borderwidth=1
            )
            name_entry.pack(fill=tk.X, pady=(0, 15))
            name_entry.focus()
            
            tk.Label(
                form_frame,
                text="Phone Number: (optional)",
                font=("Arial", 11)
            ).pack(anchor="w", pady=(0, 5))
            
            phone_entry = tk.Entry(
                form_frame,
                font=("Arial", 11),
                width=30,
                relief=tk.SOLID,
                borderwidth=1
            )
            phone_entry.pack(fill=tk.X, pady=(0, 20))
            
            result = {'proceed': False}
            
            def submit_customer():
                name = name_entry.get().strip()
                if not name:
                    messagebox.showerror(
                        "Required Field",
                        "Customer name is required for credit sales",
                        parent=customer_dialog
                    )
                    return
                
                result['name'] = name
                result['phone'] = phone_entry.get().strip() or None
                result['proceed'] = True
                customer_dialog.destroy()
            
            btn_frame = tk.Frame(form_frame)
            btn_frame.pack(fill=tk.X)
            
            tk.Button(
                btn_frame,
                text="Continue",
                font=("Arial", 11, "bold"),
                bg="#27ae60",
                fg="white",
                padx=20,
                pady=8,
                relief=tk.FLAT,
                cursor="hand2",
                command=submit_customer
            ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
            
            tk.Button(
                btn_frame,
                text="Cancel",
                font=("Arial", 11),
                bg="#95a5a6",
                fg="white",
                padx=20,
                pady=8,
                relief=tk.FLAT,
                cursor="hand2",
                command=customer_dialog.destroy
            ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))
            
            customer_dialog.bind('<Return>', lambda e: submit_customer())
            customer_dialog.bind('<Escape>', lambda e: customer_dialog.destroy())
            
            self.root.wait_window(customer_dialog)
            
            if not result.get('proceed'):
                return
            
            customer_name = result['name']
            customer_phone = result.get('phone')
        
        # Confirm sale
        subtotal = sum(item['subtotal'] for item in self.cart_items)
        final_amount = subtotal - self.discount_amount
        
        confirm_msg = f"Confirm {payment_method.upper()} Sale\n\n"
        confirm_msg += f"Items: {len(self.cart_items)}\n"
        confirm_msg += f"Subtotal: ₹{subtotal:.2f}\n"
        if self.discount_amount > 0:
            confirm_msg += f"Discount: -₹{self.discount_amount:.2f}\n"
        confirm_msg += f"\nFINAL AMOUNT: ₹{final_amount:.2f}\n"
        
        if customer_name:
            confirm_msg += f"\nCustomer: {customer_name}"
        
        if not messagebox.askyesno("Confirm Sale", confirm_msg, parent=self.root):
            return
        
        # Create sale
        messagebox.showinfo(
            "Sale Completed",
            f"✓ Sale completed successfully!\n\nAmount: ₹{final_amount:.2f}",
            parent=self.root
        )
        
        # Clear cart
        self.clear_cart()
        self.load_products()
        self.update_today_summary()
    
    def clear_cart(self):
        """Clear shopping cart"""
        if self.cart_items:
            if not messagebox.askyesno(
                "Clear Cart",
                "Are you sure you want to clear the cart?",
                parent=self.root
            ):
                return
        
        self.cart_items = []
        self.discount_amount = 0
        self.discount_reason = ""
        self.cart_tree.delete(*self.cart_tree.get_children())
        self.update_totals()
    
    def update_today_summary(self):
        """Update today's summary labels"""
        try:
            summary = db.get_today_summary()
            
            if summary:
                self.summary_sales_label.config(text=f"₹{summary['total_sales']:.2f}")
                self.summary_trans_label.config(text=str(summary['total_transactions']))
                self.summary_cash_label.config(text=f"₹{summary['cash_sales']:.2f}")
                self.summary_credit_label.config(text=f"₹{summary['credit_sales']:.2f}")
        except:
            pass
    
    def add_product_quick(self):
        """Quick add product dialog"""
        if PRODUCT_MANAGER_AVAILABLE:
            ProductManagerWindow(self.root, self.user_data)
            self.load_products()
        else:
            messagebox.showinfo(
                "Module Not Available",
                "Product management module not loaded.",
                parent=self.root
            )
    
    def manage_products(self):
        """Open product management window"""
        if PRODUCT_MANAGER_AVAILABLE:
            ProductManagerWindow(self.root, self.user_data)
            self.load_products()
        else:
            messagebox.showinfo(
                "Module Not Available",
                "Product management module not loaded.",
                parent=self.root
            )
    
    def manage_stock_dialog(self):
        """Show stock management dialog (Admin only)"""
        if STOCK_MANAGER_AVAILABLE:
            StockManagerWindow(self.root, self.user_data)
            self.load_products()
        else:
            messagebox.showinfo(
                "Module Not Available",
                "Stock management module not loaded.",
                parent=self.root
            )
    
    def show_reports(self):
        """Show reports window"""
        if REPORTS_AVAILABLE:
            ReportsWindow(self.root, self.user_data)
        else:
            messagebox.showinfo(
                "Module Not Available",
                "Reports module not loaded.",
                parent=self.root
            )
    
    def show_stock_status(self):
        """Show current stock status"""
        stock_window = tk.Toplevel(self.root)
        stock_window.title("Current Stock Status")
        stock_window.geometry("900x600")
        
        # Center window
        stock_window.update_idletasks()
        x = (stock_window.winfo_screenwidth() // 2) - (stock_window.winfo_width() // 2)
        y = (stock_window.winfo_screenheight() // 2) - (stock_window.winfo_height() // 2)
        stock_window.geometry(f"+{x}+{y}")
        
        # Header
        header = tk.Frame(stock_window, bg="#3498db")
        header.pack(fill=tk.X)
        
        tk.Label(
            header,
            text="📦 Current Stock Status",
            font=("Arial", 16, "bold"),
            bg="#3498db",
            fg="white"
        ).pack(pady=15)
        
        # Create treeview
        frame = tk.Frame(stock_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('code', 'name', 'quality', 'kg', 'bags', 'status')
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        tree.heading('code', text='Product Code')
        tree.heading('name', text='Product Name')
        tree.heading('quality', text='Quality')
        tree.heading('kg', text='Stock (kg)')
        tree.heading('bags', text='Bags')
        tree.heading('status', text='Status')
        
        tree.column('code', width=120)
        tree.column('name', width=200)
        tree.column('quality', width=100)
        tree.column('kg', width=100)
        tree.column('bags', width=80)
        tree.column('status', width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Color coding
        tree.tag_configure('low', background='#ffcccc')
        tree.tag_configure('out', background='#ff9999')
        tree.tag_configure('ok', background='#ccffcc')
        
        # Load stock data
        try:
            stock_data = db.get_all_stock_status()
            
            for item in stock_data:
                tag = 'ok'
                if item['stock_status'] == 'Out of Stock':
                    tag = 'out'
                elif item['stock_status'] == 'Low Stock':
                    tag = 'low'
                
                tree.insert('', tk.END, values=(
                    item['product_code'],
                    item['name'],
                    item['quality'].title(),
                    f"{item['quantity_kg']:.2f}",
                    item['quantity_bags'],
                    item['stock_status']
                ), tags=(tag,))
        except:
            pass
        
        # Button
        tk.Button(
            stock_window,
            text="Close",
            font=("Arial", 11),
            bg="#95a5a6",
            fg="white",
            padx=30,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
            command=stock_window.destroy
        ).pack(pady=10)
    
    def show_today_detailed_summary(self):
        """Show detailed today's summary"""
        try:
            summary = db.get_today_summary()
            
            msg = "=" * 40 + "\n"
            msg += "   TODAY'S DETAILED SUMMARY\n"
            msg += "=" * 40 + "\n\n"
            
            if summary:
                msg += f"Total Sales: ₹{summary['total_sales']:.2f}\n"
                msg += f"Total Transactions: {summary['total_transactions']}\n"
                msg += f"Total Discount: ₹{summary['total_discount']:.2f}\n\n"
                msg += f"Cash Sales: ₹{summary['cash_sales']:.2f}\n"
                msg += f"Credit Sales: ₹{summary['credit_sales']:.2f}\n"
            else:
                msg += "No sales recorded today\n"
            
            msg += "\n" + "=" * 40
            
            messagebox.showinfo("Today's Summary", msg, parent=self.root)
        except:
            messagebox.showinfo("Today's Summary", "Unable to retrieve summary data", parent=self.root)
    
    def backup_database(self):
        """Create database backup"""
        try:
            import shutil
            from datetime import datetime
            
            # Create backups directory if not exists
            if not os.path.exists('backups'):
                os.makedirs('backups')
            
            # Generate backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"backups/ricemill_pos_backup_{timestamp}.db"
            
            # Copy database
            shutil.copy2('ricemill_pos.db', backup_file)
            
            messagebox.showinfo(
                "Backup Successful",
                f"Database backed up successfully!\n\nFile: {backup_file}",
                parent=self.root
            )
        except Exception as e:
            messagebox.showerror(
                "Backup Failed",
                f"Failed to create backup:\n{str(e)}",
                parent=self.root
            )
    
    def show_database_info(self):
        """Show database information"""
        try:
            db_size = os.path.getsize('ricemill_pos.db') / (1024 * 1024)
            products_count = db.fetch_one("SELECT COUNT(*) as count FROM products")['count']
            sales_count = db.fetch_one("SELECT COUNT(*) as count FROM sales")['count']
            users_count = db.fetch_one("SELECT COUNT(*) as count FROM users")['count']
            
            msg = "📊 Database Information\n"
            msg += "=" * 40 + "\n"
            msg += f"Database Size: {db_size:.2f} MB\n"
            msg += f"Total Products: {products_count}\n"
            msg += f"Total Sales: {sales_count}\n"
            msg += f"Total Users: {users_count}\n"
            
            messagebox.showinfo("Database Info", msg, parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get database info:\n{str(e)}", parent=self.root)
    
    def export_data_dialog(self):
        """Show export data dialog"""
        messagebox.showinfo(
            "Export Data",
            "Use Reports menu to export:\n\n• Sales data to CSV\n• Product performance to CSV\n• Stock status to CSV",
            parent=self.root
        )
    
    def show_user_guide(self):
        """Show user guide"""
        guide = """RICE MILL POS - USER GUIDE

MAKING A SALE:
1. Select product from list
2. Click 'Add to Cart' or press F2
3. Choose sale type (by kg or by bag)
4. Enter quantity
5. Click 'Add to Cart'
6. Repeat for more items
7. Apply discount if needed (Admin only)
8. Click 'Cash Sale' or 'Credit Sale'

KEYBOARD SHORTCUTS:
F1 - New Sale (Clear Cart)
F2 - Add selected product to cart
F5 - Refresh product list
ESC - Clear cart

MANAGING STOCK (Admin):
• Menu → Products → Manage Stock
• Select product and choose:
  - Restock: Add new inventory
  - Adjust: Correct errors

REPORTS:
• Menu → Reports → Sales Reports
• View today's summary
• Export data to CSV

For more help, contact your system administrator.
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("User Guide")
        help_window.geometry("600x500")
        
        # Center window
        help_window.update_idletasks()
        x = (help_window.winfo_screenwidth() // 2) - (help_window.winfo_width() // 2)
        y = (help_window.winfo_screenheight() // 2) - (help_window.winfo_height() // 2)
        help_window.geometry(f"+{x}+{y}")
        
        text = tk.Text(help_window, font=("Courier", 10), wrap=tk.WORD, padx=20, pady=20)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert('1.0', guide)
        text.config(state=tk.DISABLED)
        
        tk.Button(
            help_window,
            text="Close",
            font=("Arial", 11),
            command=help_window.destroy
        ).pack(pady=10)
    
    def show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts = """KEYBOARD SHORTCUTS

F1    - New Sale (Clear Cart)
F2    - Add Product to Cart
F5    - Refresh Product List
ESC   - Clear Cart
Enter - Confirm dialogs
        """
        messagebox.showinfo("Keyboard Shortcuts", shortcuts, parent=self.root)
    
    def show_about(self):
        """Show about dialog"""
        about = """🌾 RICE MILL POS SYSTEM
Version 1.0

Complete offline Point of Sale system
for small rice mill businesses.

Built with Python and Tkinter.
        """
        messagebox.showinfo(
            "About Rice Mill POS",
            about,
            parent=self.root
        )
    
    def logout(self):
        """Logout and return to login"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?", parent=self.root):
            self.root.destroy()
    
    def on_closing(self):
        """Handle window close"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?", parent=self.root):
            self.root.destroy()


def main():
    """Main application entry point"""
    root = tk.Tk()
    
    # Show login window
    login = LoginWindow(root)
    root.mainloop()
    
    # If login successful, show main application
    if login.user_data:
        app_root = tk.Tk()
        app = POSApplication(app_root, login.user_data)
        app_root.mainloop()


if __name__ == "__main__":
    main()
