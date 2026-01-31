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

# Optional modules
try:
    from stock_manager import StockManagerWindow
    STOCK_MANAGER_AVAILABLE = True
except Exception:
    STOCK_MANAGER_AVAILABLE = False

try:
    from product_manager import ProductManagerWindow
    PRODUCT_MANAGER_AVAILABLE = True
except Exception:
    PRODUCT_MANAGER_AVAILABLE = False

try:
    from reports import ReportsWindow
    REPORTS_AVAILABLE = True
except Exception:
    REPORTS_AVAILABLE = False


class LoginWindow:
    """Simple login window"""
    def __init__(self, root):
        self.root = root
        self.root.title("Rice Mill POS - Login")
        self.root.geometry("400x300")
        self.user_data = None

        self.create_widgets()
        self.center_window()

    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def create_widgets(self):
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Username:", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=8)
        self.username_entry = tk.Entry(frame, font=("Arial", 11))
        self.username_entry.grid(row=0, column=1, pady=8)

        tk.Label(frame, text="Password:", font=("Arial", 11)).grid(row=1, column=0, sticky="w", pady=8)
        self.password_entry = tk.Entry(frame, show="●", font=("Arial", 11))
        self.password_entry.grid(row=1, column=1, pady=8)

        btn = tk.Button(frame, text="Login", bg="#27ae60", fg="white", command=self.login)
        btn.grid(row=2, column=0, columnspan=2, pady=12)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Login Error", "Please enter username and password", parent=self.root)
            return

        user = db.authenticate_user(username, password)
        if user:
            self.user_data = user
            self.root.destroy()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials", parent=self.root)
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
        self.update_cash_drawer()
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
        file_menu.add_command(label="Cash Payout", command=self.open_payout_window)
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
            label="Payout History", 
            command=self.show_payout_history
        )
        tools_menu.add_separator()
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
            text="Subtotal: RS.0.00",
            font=("Arial", 13),
            bg="#ecf0f1",
            anchor="e"
        )
        self.subtotal_label.pack(fill=tk.X, padx=15, pady=(10, 5))
        
        self.discount_label = tk.Label(
            total_frame,
            text="Discount: RS.0.00",
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
            text="TOTAL: RS.0.00",
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
        
        tk.Button(
            checkout_frame,
            text="💵 CASH PAYMENT",
            font=("Arial", 13, "bold"),
            bg="#27ae60",
            fg="white",
            padx=25,
            pady=15,
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self.checkout('cash')
        ).pack(fill=tk.X)
        
        # Cash Drawer Panel - Main Cash Interface
        cash_drawer_panel = tk.Frame(self.root, bg="#2c3e50", relief=tk.RAISED, borderwidth=2)
        cash_drawer_panel.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(5, 0))
        
        # Header
        tk.Label(
            cash_drawer_panel,
            text="💳 CASH DRAWER - TODAY",
            font=("Arial", 13, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack(fill=tk.X, padx=15, pady=(10, 5))
        
        # Cash stats frame
        cash_stats_frame = tk.Frame(cash_drawer_panel, bg="#2c3e50")
        cash_stats_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Cash sales
        cash_sales_frame = tk.Frame(cash_stats_frame, bg="#27ae60", relief=tk.RAISED, borderwidth=1)
        cash_sales_frame.pack(side=tk.LEFT, padx=(0, 8), ipadx=20, ipady=10, fill=tk.X, expand=True)
        
        tk.Label(
            cash_sales_frame,
            text="Cash Sales",
            font=("Arial", 10, "bold"),
            bg="#27ae60",
            fg="white"
        ).pack()
        
        self.cash_drawer_sales_label = tk.Label(
            cash_sales_frame,
            text="RS.0.00",
            font=("Arial", 14, "bold"),
            bg="#27ae60",
            fg="white"
        )
        self.cash_drawer_sales_label.pack(pady=(5, 0))
        
        # Payouts
        payout_frame = tk.Frame(cash_stats_frame, bg="#e74c3c", relief=tk.RAISED, borderwidth=1)
        payout_frame.pack(side=tk.LEFT, padx=(0, 8), ipadx=20, ipady=10, fill=tk.X, expand=True)
        
        tk.Label(
            payout_frame,
            text="Payouts",
            font=("Arial", 10, "bold"),
            bg="#e74c3c",
            fg="white"
        ).pack()
        
        self.cash_drawer_payout_label = tk.Label(
            payout_frame,
            text="RS.0.00",
            font=("Arial", 14, "bold"),
            bg="#e74c3c",
            fg="white"
        )
        self.cash_drawer_payout_label.pack(pady=(5, 0))
        
        # Net cash (Sales - Payouts)
        net_cash_frame = tk.Frame(cash_stats_frame, bg="#f39c12", relief=tk.RAISED, borderwidth=1)
        net_cash_frame.pack(side=tk.LEFT, ipadx=20, ipady=10, fill=tk.X, expand=True)
        
        tk.Label(
            net_cash_frame,
            text="Net Cash",
            font=("Arial", 10, "bold"),
            bg="#f39c12",
            fg="white"
        ).pack()
        
        self.cash_drawer_net_label = tk.Label(
            net_cash_frame,
            text="RS.0.00",
            font=("Arial", 14, "bold"),
            bg="#f39c12",
            fg="white"
        )
        self.cash_drawer_net_label.pack(pady=(5, 0))
        
        # Buttons frame
        cash_buttons_frame = tk.Frame(cash_drawer_panel, bg="#2c3e50")
        cash_buttons_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        tk.Button(
            cash_buttons_frame,
            text="🔄 Refresh Cash Status",
            font=("Arial", 10, "bold"),
            bg="#3498db",
            fg="white",
            padx=15,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.update_cash_drawer
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(
            cash_buttons_frame,
            text="📋 View Payout History",
            font=("Arial", 10, "bold"),
            bg="#9b59b6",
            fg="white",
            padx=15,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.show_payout_history
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(
            cash_buttons_frame,
            text="💸 New Payout",
            font=("Arial", 10, "bold"),
            bg="#e74c3c",
            fg="white",
            padx=15,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.open_payout_window
        ).pack(side=tk.LEFT)
        
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
            "RS.0.00",
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
            "RS.0.00",
            "#f39c12",
            "summary_cash"
        )
        
        self.create_summary_card(
            summary_frame,
            "📄 Credit",
            "RS.0.00",
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
    
    def load_products(self):
        """Load products into listbox"""
        self.products_listbox.delete(0, tk.END)
        self.products = db.get_all_products()
        
        # Store display mapping for proper product lookup
        self.product_display_map = {}
        
        for idx, product in enumerate(self.products):
            stock = db.get_stock_by_product(product['id'])
            stock_info = f" ({stock['quantity_kg']:.1f}kg, {stock['quantity_bags']} bags)" if stock else " (Out of Stock)"
            
            display = f"{product['name']} - RS.{product['price_per_kg']:.2f}/kg{stock_info}"
            self.products_listbox.insert(tk.END, display)
            self.product_display_map[display] = product
        
        # Clear search
        self.search_var.set("")
    
    def filter_products(self, *args):
        """Filter products based on search term"""
        search_term = self.search_var.get().lower()
        
        self.products_listbox.delete(0, tk.END)
        self.filtered_products = []
        
        for product in self.products:
            product_text = f"{product['name']} {product['quality']} {product['product_code']}".lower()
            
            if search_term in product_text:
                stock = db.get_stock_by_product(product['id'])
                stock_info = f" ({stock['quantity_kg']:.1f}kg, {stock['quantity_bags']} bags)" if stock else " (Out of Stock)"
                
                display = f"{product['name']} - RS.{product['price_per_kg']:.2f}/kg{stock_info}"
                self.products_listbox.insert(tk.END, display)
                self.filtered_products.append(product)
    
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
        
        selected_index = selection[0]
        
        # Get product from either filtered or full list
        search_term = self.search_var.get().lower()
        if search_term:
            # Using filtered list
            if selected_index >= len(self.filtered_products):
                messagebox.showerror("Error", "Product not found", parent=self.root)
                return
            product = self.filtered_products[selected_index]
        else:
            # Using full list
            if selected_index >= len(self.products):
                messagebox.showerror("Error", "Product not found", parent=self.root)
                return
            product = self.products[selected_index]
        
        # Check if product has valid data
        try:
            product_id = product['id']
            product_name = product['name']
            price_per_kg = product['price_per_kg']
        except (KeyError, IndexError, TypeError, AttributeError):
            messagebox.showerror("Error", "Invalid product selected", parent=self.root)
            return
        
        # Check stock before showing dialog
        stock = db.get_stock_by_product(product_id)
        if not stock or (stock['quantity_kg'] == 0 and stock['quantity_bags'] == 0):
            messagebox.showerror(
                "Out of Stock",
                f"{product_name} is currently out of stock",
                parent=self.root
            )
            return
        
        # Dialog to choose sale type and quantity
        dialog = tk.Toplevel(self.root)
        dialog.title("Add to Cart")
        dialog.geometry("400x320")
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
            text=f"📦 {product_name}",
            font=("Arial", 14, "bold"),
            bg="#3498db",
            fg="white"
        ).pack(pady=15)
        
        # Form
        form_frame = tk.Frame(dialog, padx=30, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Stock info
        tk.Label(
            form_frame,
            text=f"Available Stock: {stock['quantity_kg']:.1f}kg / {stock['quantity_bags']} bags",
            font=("Arial", 10, "bold"),
            fg="#27ae60"
        ).pack(anchor="w", pady=(0, 15))
        
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
            text=f"By Kilogram - RS.{price_per_kg:.2f}/kg",
            variable=sale_type_var,
            value="by_kg",
            font=("Arial", 10)
        ).pack(anchor=tk.W, pady=2)
        
        # Check if bag pricing is available
        try:
            bag_size_kg = product['bag_size_kg']
            price_per_bag = product['price_per_bag']
            if bag_size_kg and price_per_bag:
                tk.Radiobutton(
                    type_frame,
                    text=f"By Bag ({bag_size_kg}kg) - RS.{price_per_bag:.2f}/bag",
                    variable=sale_type_var,
                    value="by_bag",
                    font=("Arial", 10)
                ).pack(anchor=tk.W, pady=2)
        except (KeyError, TypeError):
            pass
        
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
        quantity_entry.select_range(0, tk.END)

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
                quantity_var.get(),
                stock
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
        
        # Bind Enter key
        dialog.bind('<Return>', lambda e: self.confirm_add_to_cart(
            dialog,
            product,
            sale_type_var.get(),
            quantity_var.get(),
            stock
        ))
    
    def confirm_add_to_cart(self, dialog, product, sale_type, quantity_str, stock):
        """Confirm adding product to cart"""
        try:
            quantity = float(quantity_str)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError as e:
            messagebox.showerror(
                "Invalid Quantity",
                f"Please enter a valid positive number for quantity",
                parent=dialog
            )
            return
        
        # Recheck stock (in case it changed)
        try:
            product_id = product['id']
            product_name = product['name']
        except (KeyError, TypeError):
            messagebox.showerror("Error", "Invalid product data", parent=dialog)
            return
        
        current_stock = db.get_stock_by_product(product_id)
        if not current_stock:
            messagebox.showerror(
                "Out of Stock",
                "This product is currently out of stock",
                parent=dialog
            )
            return
        
        try:
            price_per_kg = product['price_per_kg']
            price_per_bag = product['price_per_bag']
        except (KeyError, TypeError):
            messagebox.showerror("Error", "Invalid product pricing", parent=dialog)
            return
        
        if sale_type == 'by_kg':
            if quantity > current_stock['quantity_kg']:
                messagebox.showerror(
                    "Insufficient Stock",
                    f"Only {current_stock['quantity_kg']:.1f} kg available in stock",
                    parent=dialog
                )
                return
            price = price_per_kg
            qty_display = f"{quantity:.2f} kg"
        else:  # by_bag
            quantity = int(quantity)
            if quantity > current_stock['quantity_bags']:
                messagebox.showerror(
                    "Insufficient Stock",
                    f"Only {current_stock['quantity_bags']} bags available in stock",
                    parent=dialog
                )
                return
            price = price_per_bag if price_per_bag else price_per_kg
            qty_display = f"{quantity} bags"

        subtotal = price * quantity
        
        try:
            quality = product['quality']
        except (KeyError, TypeError):
            quality = 'Standard'
        
        cart_item = {
            'product_id': product_id,
            'product_name': product_name,
            'quality': quality,
            'sale_type': sale_type,
            'quantity': quantity,
            'price': price,
            'subtotal': subtotal
        }
        
        self.cart_items.append(cart_item)
        self.refresh_cart()
        dialog.destroy()
        
        messagebox.showinfo(
            "Added to Cart",
            f"✓ {product_name} added successfully!",
            parent=self.root
        )
    
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
                f"RS.{item['price']:.2f}",
                f"RS.{item['subtotal']:.2f}"
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
        
        self.subtotal_label.config(text=f"Subtotal: RS.{subtotal:.2f}")
        self.discount_label.config(text=f"Discount: -RS.{self.discount_amount:.2f}")
        
        total = subtotal - self.discount_amount
        self.total_label.config(text=f"TOTAL: RS.{total:.2f}")
    
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
            text=f"Price: RS.{item['price']:.2f}",
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
            f"Enter discount amount:\n\nSubtotal: RS.{subtotal:.2f}\nMax discount: RS.{subtotal:.2f}",
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
                    f"Discount of RS.{discount:.2f} applied successfully",
                    parent=self.root
                )
            else:
                messagebox.showwarning(
                    "Reason Required",
                    "Discount reason is required",
                    parent=self.root
                )
    
    def checkout(self, payment_method='cash'):
        """Process cash payment checkout"""
        if not self.cart_items:
            messagebox.showwarning("Empty Cart", "Cannot checkout with empty cart", parent=self.root)
            return
        
        # Confirm sale
        subtotal = sum(item['subtotal'] for item in self.cart_items)
        final_amount = subtotal - self.discount_amount
        
        confirm_msg = f"Confirm CASH Payment\n\n"
        confirm_msg += f"Items: {len(self.cart_items)}\n"
        confirm_msg += f"Subtotal: RS.{subtotal:.2f}\n"
        if self.discount_amount > 0:
            confirm_msg += f"Discount: -RS.{self.discount_amount:.2f}\n"
        confirm_msg += f"\nFINAL AMOUNT: RS.{final_amount:.2f}\n"
        
        if not messagebox.askyesno("Confirm Payment", confirm_msg, parent=self.root):
            return
        
        # Create sale
        messagebox.showinfo(
            "Payment Completed",
            f"✓ Payment completed successfully!\n\nAmount: RS.{final_amount:.2f}",
            parent=self.root
        )
        
        # Clear cart
        self.clear_cart()
        self.load_products()
        self.update_today_summary()
        self.update_cash_drawer()
    
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
                self.summary_sales_label.config(text=f"RS.{summary['total_sales']:.2f}")
                self.summary_trans_label.config(text=str(summary['total_transactions']))
                self.summary_cash_label.config(text=f"RS.{summary['cash_sales']:.2f}")
                self.summary_credit_label.config(text=f"RS.{summary['credit_sales']:.2f}")
        except:
            pass
    
    def update_cash_drawer(self):
        """Update cash drawer display with today's totals"""
        try:
            summary = db.get_today_summary()
            total_payouts = db.get_total_payouts_today()
            
            if summary:
                cash_sales = summary['cash_sales']
            else:
                cash_sales = 0
            
            net_cash = cash_sales - total_payouts
            
            # Update labels
            self.cash_drawer_sales_label.config(text=f"RS.{cash_sales:.2f}")
            self.cash_drawer_payout_label.config(text=f"RS.{total_payouts:.2f}")
            self.cash_drawer_net_label.config(text=f"RS.{net_cash:.2f}")
        except Exception as e:
            print(f"Error updating cash drawer: {str(e)}")
    
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
            self.load_products
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
                msg += f"Total Sales: RS.{summary['total_sales']:.2f}\n"
                msg += f"Total Transactions: {summary['total_transactions']}\n"
                msg += f"Total Discount: RS.{summary['total_discount']:.2f}\n\n"
                msg += f"Cash Sales: RS.{summary['cash_sales']:.2f}\n"
                msg += f"Credit Sales: RS.{summary['credit_sales']:.2f}\n"
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
    
    def show_reports(self):
        """Show reports window"""
        if REPORTS_AVAILABLE:
            ReportsWindow(self.root, self.user_data)
        else:
            messagebox.showinfo(
                "Reports",
                "Reports module is not available.",
                parent=self.root
            )
    
    def show_stock_status(self):
        """Show stock status report"""
        try:
            stock_status = db.get_all_stock_status()
            
            if not stock_status:
                messagebox.showinfo("Stock Status", "No products found", parent=self.root)
                return
            
            # Create a window to display stock status
            stock_window = tk.Toplevel(self.root)
            stock_window.title("Stock Status Report")
            stock_window.geometry("900x500")
            
            # Center window
            stock_window.update_idletasks()
            x = (stock_window.winfo_screenwidth() // 2) - (stock_window.winfo_width() // 2)
            y = (stock_window.winfo_screenheight() // 2) - (stock_window.winfo_height() // 2)
            stock_window.geometry(f"+{x}+{y}")
            
            # Header
            header = tk.Label(
                stock_window,
                text="📦 Stock Status Report",
                font=("Arial", 14, "bold"),
                bg="#27ae60",
                fg="white",
                pady=10
            )
            header.pack(fill=tk.X)
            
            # Create treeview for stock data
            tree_frame = tk.Frame(stock_window)
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Scrollbar
            scrollbar = tk.Scrollbar(tree_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Treeview
            style = ttk.Style()
            style.configure("Stock.Treeview", rowheight=25, font=("Arial", 10))
            style.configure("Stock.Treeview.Heading", font=("Arial", 11, "bold"))
            
            columns = ('product', 'quality', 'stock_kg', 'stock_bags', 'status', 'price_kg')
            tree = ttk.Treeview(
                tree_frame,
                columns=columns,
                show='headings',
                style="Stock.Treeview",
                yscrollcommand=scrollbar.set
            )
            
            tree.heading('product', text='Product Name')
            tree.heading('quality', text='Quality')
            tree.heading('stock_kg', text='Stock (kg)')
            tree.heading('stock_bags', text='Stock (bags)')
            tree.heading('status', text='Status')
            tree.heading('price_kg', text='Price/kg (RS.)')
            
            tree.column('product', width=200)
            tree.column('quality', width=100)
            tree.column('stock_kg', width=100)
            tree.column('stock_bags', width=100)
            tree.column('status', width=150)
            tree.column('price_kg', width=100)
            
            scrollbar.config(command=tree.yview)
            
            # Add data to treeview
            for stock in stock_status:
                status = stock['stock_status']
                tag = 'low_stock' if status == 'Low Stock' else 'out_of_stock' if status == 'Out of Stock' else 'available'
                
                tree.insert('', 'end', values=(
                    stock['name'],
                    stock['quality'],
                    f"{stock['quantity_kg']:.1f}",
                    stock['quantity_bags'],
                    status,
                    f"{stock['price_per_kg']:.2f}"
                ), tags=(tag,))
            
            # Configure tags for coloring
            tree.tag_configure('available', foreground='green')
            tree.tag_configure('low_stock', foreground='orange')
            tree.tag_configure('out_of_stock', foreground='red')
            
            tree.pack(fill=tk.BOTH, expand=True)
            
            # Close button
            tk.Button(
                stock_window,
                text="Close",
                font=("Arial", 11),
                bg="#e74c3c",
                fg="white",
                padx=20,
                pady=8,
                relief=tk.FLAT,
                cursor="hand2",
                command=stock_window.destroy
            ).pack(pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load stock status:\n{str(e)}", parent=self.root)
    
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
    
    def open_payout_window(self):
        """Open cash payout window"""
        payout_window = tk.Toplevel(self.root)
        payout_window.title("Cash Payout")
        payout_window.geometry("500x450")
        payout_window.transient(self.root)
        payout_window.resizable(False, False)
        
        # Center window
        payout_window.update_idletasks()
        x = (payout_window.winfo_screenwidth() // 2) - (payout_window.winfo_width() // 2)
        y = (payout_window.winfo_screenheight() // 2) - (payout_window.winfo_height() // 2)
        payout_window.geometry(f"+{x}+{y}")
        
        # Header
        header = tk.Frame(payout_window, bg="#e74c3c", height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="💸 Cash Payout Request",
            font=("Arial", 16, "bold"),
            bg="#e74c3c",
            fg="white"
        ).pack(pady=15)
        
        # Form frame
        form_frame = tk.Frame(payout_window, padx=30, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Amount
        tk.Label(
            form_frame,
            text="Payout Amount (RS.): *",
            font=("Arial", 11, "bold"),
            bg=payout_window.cget('bg')
        ).pack(anchor="w", pady=(0, 5))
        
        amount_var = tk.StringVar()
        amount_entry = tk.Entry(
            form_frame,
            textvariable=amount_var,
            font=("Arial", 12),
            width=30,
            relief=tk.SOLID,
            borderwidth=1
        )
        amount_entry.pack(fill=tk.X, pady=(0, 15))
        amount_entry.focus()
        
        # Reason
        tk.Label(
            form_frame,
            text="Reason for Payout: *",
            font=("Arial", 11, "bold"),
            bg=payout_window.cget('bg')
        ).pack(anchor="w", pady=(0, 5))
        
        reason_var = tk.StringVar()
        reason_frame = tk.Frame(form_frame)
        reason_frame.pack(fill=tk.X, pady=(0, 15))
        
        reasons = [
            "Daily Expenses",
            "Supplier Payment",
            "Salary/Wages",
            "Maintenance",
            "Other"
        ]
        
        for reason in reasons:
            tk.Radiobutton(
                reason_frame,
                text=reason,
                variable=reason_var,
                value=reason,
                font=("Arial", 10)
            ).pack(anchor="w", pady=2)
        
        reason_var.set("Daily Expenses")
        
        # Notes
        tk.Label(
            form_frame,
            text="Additional Notes: (optional)",
            font=("Arial", 11, "bold"),
            bg=payout_window.cget('bg')
        ).pack(anchor="w", pady=(0, 5))
        
        notes_text = tk.Text(
            form_frame,
            font=("Arial", 10),
            height=3,
            width=40,
            relief=tk.SOLID,
            borderwidth=1
        )
        notes_text.pack(fill=tk.X, pady=(0, 20))
        
        # Buttons
        btn_frame = tk.Frame(form_frame)
        btn_frame.pack(fill=tk.X)
        
        def process_payout():
            amount_str = amount_var.get().strip()
            reason = reason_var.get().strip()
            notes = notes_text.get("1.0", tk.END).strip() or None
            
            if not amount_str:
                messagebox.showerror("Required Field", "Please enter payout amount", parent=payout_window)
                return
            
            if not reason:
                messagebox.showerror("Required Field", "Please select a reason", parent=payout_window)
                return
            
            try:
                amount = float(amount_str)
                if amount <= 0:
                    messagebox.showerror("Invalid Amount", "Amount must be greater than 0", parent=payout_window)
                    return
            except ValueError:
                messagebox.showerror("Invalid Amount", "Please enter a valid number", parent=payout_window)
                return
            
            # Confirm payout
            confirm_msg = f"Confirm Cash Payout?\n\n"
            confirm_msg += f"Amount: RS.{amount:.2f}\n"
            confirm_msg += f"Reason: {reason}\n"
            if notes:
                confirm_msg += f"Notes: {notes}\n"
            
            if not messagebox.askyesno("Confirm Payout", confirm_msg, parent=payout_window):
                return
            
            # Process payout
            try:
                db.create_payout(amount, reason, self.user_data['id'], notes)
                messagebox.showinfo(
                    "Payout Successful",
                    f"✓ Payout of RS.{amount:.2f} has been recorded.",
                    parent=payout_window
                )
                payout_window.destroy()
                self.update_today_summary()
                self.update_cash_drawer()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process payout:\n{str(e)}", parent=payout_window)
        
        tk.Button(
            btn_frame,
            text="✓ Process Payout",
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
            command=process_payout
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        
        tk.Button(
            btn_frame,
            text="✕ Cancel",
            font=("Arial", 11),
            bg="#95a5a6",
            fg="white",
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2",
            command=payout_window.destroy
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))
    
    def show_payout_history(self):
        """Show payout history window"""
        try:
            payouts = db.get_all_payouts()
            
            # Create window
            history_window = tk.Toplevel(self.root)
            history_window.title("Payout History")
            history_window.geometry("900x500")
            
            # Center window
            history_window.update_idletasks()
            x = (history_window.winfo_screenwidth() // 2) - (history_window.winfo_width() // 2)
            y = (history_window.winfo_screenheight() // 2) - (history_window.winfo_height() // 2)
            history_window.geometry(f"+{x}+{y}")
            
            # Header
            header = tk.Label(
                history_window,
                text="💸 Payout History",
                font=("Arial", 14, "bold"),
                bg="#e74c3c",
                fg="white",
                pady=10
            )
            header.pack(fill=tk.X)
            
            # Create treeview for payout data
            tree_frame = tk.Frame(history_window)
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Scrollbar
            scrollbar = tk.Scrollbar(tree_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Treeview
            style = ttk.Style()
            style.configure("Payout.Treeview", rowheight=25, font=("Arial", 10))
            style.configure("Payout.Treeview.Heading", font=("Arial", 11, "bold"))
            
            columns = ('date', 'amount', 'reason', 'authorized_by', 'notes')
            tree = ttk.Treeview(
                tree_frame,
                columns=columns,
                show='headings',
                style="Payout.Treeview",
                yscrollcommand=scrollbar.set
            )
            
            tree.heading('date', text='Date & Time')
            tree.heading('amount', text='Amount (RS.)')
            tree.heading('reason', text='Reason')
            tree.heading('authorized_by', text='Authorized By')
            tree.heading('notes', text='Notes')
            
            tree.column('date', width=180)
            tree.column('amount', width=120)
            tree.column('reason', width=150)
            tree.column('authorized_by', width=120)
            tree.column('notes', width=200)
            
            scrollbar.config(command=tree.yview)
            
            # Add data to treeview
            total_payouts = 0
            for payout in payouts:
                tree.insert('', 'end', values=(
                    payout['payout_date'],
                    f"RS.{payout['amount']:.2f}",
                    payout['reason'],
                    payout['authorized_by_name'],
                    payout['notes'] if payout['notes'] else "-"
                ))
                total_payouts += payout['amount']
            
            tree.pack(fill=tk.BOTH, expand=True)
            
            # Summary frame
            summary_frame = tk.Frame(history_window, bg="#ecf0f1", relief=tk.RIDGE, borderwidth=1)
            summary_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
            
            summary_text = f"Total Payouts: RS.{total_payouts:.2f} | Records: {len(payouts)}"
            tk.Label(
                summary_frame,
                text=summary_text,
                font=("Arial", 11, "bold"),
                bg="#ecf0f1",
                fg="#2c3e50"
            ).pack(pady=10)
            
            # Close button
            tk.Button(
                history_window,
                text="Close",
                font=("Arial", 11),
                bg="#95a5a6",
                fg="white",
                padx=20,
                pady=8,
                relief=tk.FLAT,
                cursor="hand2",
                command=history_window.destroy
            ).pack(pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load payout history:\n{str(e)}", parent=self.root)


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
