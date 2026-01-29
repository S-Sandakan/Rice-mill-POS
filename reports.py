"""
Rice Mill POS System - Reports Module
Handles sales reports, analytics, and data export
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import csv
from database import db


class ReportsWindow:
    """Reports and Analytics Window"""
    
    def __init__(self, parent, user_data):
        self.window = tk.Toplevel(parent)
        self.window.title("Reports & Analytics")
        self.window.geometry("1000x700")
        self.user_data = user_data
        
        self.create_widgets()
        self.load_today_summary()
    
    def create_widgets(self):
        """Create reports widgets"""
        # Header
        header = tk.Label(
            self.window,
            text="📊 Reports & Analytics",
            font=("Arial", 16, "bold"),
            bg="#8e44ad",
            fg="white",
            pady=10
        )
        header.pack(fill=tk.X)
        
        # Main notebook for tabs
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Today's Summary
        self.today_tab = tk.Frame(notebook)
        notebook.add(self.today_tab, text="Today's Summary")
        self.create_today_summary_tab()
        
        # Tab 2: Sales History
        self.sales_tab = tk.Frame(notebook)
        notebook.add(self.sales_tab, text="Sales History")
        self.create_sales_history_tab()
        
        # Tab 3: Date Range Reports
        self.range_tab = tk.Frame(notebook)
        notebook.add(self.range_tab, text="Date Range Report")
        self.create_date_range_tab()
        
        # Tab 4: Product Performance
        self.product_tab = tk.Frame(notebook)
        notebook.add(self.product_tab, text="Product Performance")
        self.create_product_performance_tab()
    
    def create_today_summary_tab(self):
        """Create today's summary tab"""
        # Summary cards frame
        cards_frame = tk.Frame(self.today_tab, bg="#ecf0f1")
        cards_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Sales card
        sales_card = tk.Frame(cards_frame, bg="#27ae60", relief=tk.RAISED, borderwidth=2)
        sales_card.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        tk.Label(sales_card, text="💰 Total Sales", font=("Arial", 12), bg="#27ae60", fg="white").pack(pady=5)
        self.today_sales_label = tk.Label(sales_card, text="₹0.00", font=("Arial", 20, "bold"), bg="#27ae60", fg="white")
        self.today_sales_label.pack(pady=10)
        
        # Transactions card
        trans_card = tk.Frame(cards_frame, bg="#3498db", relief=tk.RAISED, borderwidth=2)
        trans_card.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        tk.Label(trans_card, text="📝 Transactions", font=("Arial", 12), bg="#3498db", fg="white").pack(pady=5)
        self.today_trans_label = tk.Label(trans_card, text="0", font=("Arial", 20, "bold"), bg="#3498db", fg="white")
        self.today_trans_label.pack(pady=10)
        
        # Cash sales card
        cash_card = tk.Frame(cards_frame, bg="#f39c12", relief=tk.RAISED, borderwidth=2)
        cash_card.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        tk.Label(cash_card, text="💵 Cash Sales", font=("Arial", 12), bg="#f39c12", fg="white").pack(pady=5)
        self.today_cash_label = tk.Label(cash_card, text="₹0.00", font=("Arial", 20, "bold"), bg="#f39c12", fg="white")
        self.today_cash_label.pack(pady=10)
        
        # Credit sales card
        credit_card = tk.Frame(cards_frame, bg="#e74c3c", relief=tk.RAISED, borderwidth=2)
        credit_card.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        tk.Label(credit_card, text="📄 Credit Sales", font=("Arial", 12), bg="#e74c3c", fg="white").pack(pady=5)
        self.today_credit_label = tk.Label(credit_card, text="₹0.00", font=("Arial", 20, "bold"), bg="#e74c3c", fg="white")
        self.today_credit_label.pack(pady=10)
        
        # Recent sales list
        list_frame = tk.LabelFrame(self.today_tab, text="Recent Sales Today", font=("Arial", 12, "bold"))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        columns = ('sale_number', 'time', 'cashier', 'customer', 'amount', 'payment')
        self.today_sales_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        self.today_sales_tree.heading('sale_number', text='Sale #')
        self.today_sales_tree.heading('time', text='Time')
        self.today_sales_tree.heading('cashier', text='Cashier')
        self.today_sales_tree.heading('customer', text='Customer')
        self.today_sales_tree.heading('amount', text='Amount')
        self.today_sales_tree.heading('payment', text='Payment')
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.today_sales_tree.yview)
        self.today_sales_tree.configure(yscrollcommand=scrollbar.set)
        
        self.today_sales_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Buttons
        btn_frame = tk.Frame(self.today_tab)
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="🔄 Refresh",
            font=("Arial", 11),
            bg="#95a5a6",
            fg="white",
            padx=20,
            pady=8,
            command=self.load_today_summary
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="📥 Export to CSV",
            font=("Arial", 11),
            bg="#3498db",
            fg="white",
            padx=20,
            pady=8,
            command=lambda: self.export_to_csv('today')
        ).pack(side=tk.LEFT, padx=5)
    
    def create_sales_history_tab(self):
        """Create sales history tab"""
        # Controls frame
        controls_frame = tk.Frame(self.sales_tab)
        controls_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(controls_frame, text="Search:", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(controls_frame, font=("Arial", 11), width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            controls_frame,
            text="🔍 Search",
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            command=self.search_sales
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            controls_frame,
            text="Show All",
            font=("Arial", 10),
            command=self.load_sales_history
        ).pack(side=tk.LEFT, padx=5)
        
        # Sales list
        list_frame = tk.Frame(self.sales_tab)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        columns = ('id', 'sale_number', 'date', 'cashier', 'customer', 'amount', 'discount', 'final', 'payment')
        self.sales_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        self.sales_tree.heading('id', text='ID')
        self.sales_tree.heading('sale_number', text='Sale Number')
        self.sales_tree.heading('date', text='Date/Time')
        self.sales_tree.heading('cashier', text='Cashier')
        self.sales_tree.heading('customer', text='Customer')
        self.sales_tree.heading('amount', text='Amount')
        self.sales_tree.heading('discount', text='Discount')
        self.sales_tree.heading('final', text='Final Amount')
        self.sales_tree.heading('payment', text='Payment')
        
        self.sales_tree.column('id', width=50)
        self.sales_tree.column('sale_number', width=120)
        self.sales_tree.column('date', width=150)
        self.sales_tree.column('cashier', width=120)
        self.sales_tree.column('customer', width=120)
        self.sales_tree.column('amount', width=100)
        self.sales_tree.column('discount', width=80)
        self.sales_tree.column('final', width=100)
        self.sales_tree.column('payment', width=80)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=scrollbar.set)
        
        self.sales_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to view details
        self.sales_tree.bind('<Double-1>', self.view_sale_details)
        
        # Buttons
        btn_frame = tk.Frame(self.sales_tab)
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="👁️ View Details",
            font=("Arial", 11),
            bg="#3498db",
            fg="white",
            padx=20,
            pady=8,
            command=lambda: self.view_sale_details(None)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🔄 Refresh",
            font=("Arial", 11),
            bg="#95a5a6",
            fg="white",
            padx=20,
            pady=8,
            command=self.load_sales_history
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="📥 Export to CSV",
            font=("Arial", 11),
            bg="#3498db",
            fg="white",
            padx=20,
            pady=8,
            command=lambda: self.export_to_csv('all_sales')
        ).pack(side=tk.LEFT, padx=5)
        
        # Load initial data
        self.load_sales_history()
    
    def create_date_range_tab(self):
        """Create date range report tab"""
        # Date selection frame
        date_frame = tk.Frame(self.range_tab)
        date_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(date_frame, text="From Date (YYYY-MM-DD):", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
        self.from_date_entry = tk.Entry(date_frame, font=("Arial", 11), width=15)
        self.from_date_entry.pack(side=tk.LEFT, padx=5)
        self.from_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        tk.Label(date_frame, text="To Date (YYYY-MM-DD):", font=("Arial", 11)).pack(side=tk.LEFT, padx=20)
        self.to_date_entry = tk.Entry(date_frame, font=("Arial", 11), width=15)
        self.to_date_entry.pack(side=tk.LEFT, padx=5)
        self.to_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        tk.Button(
            date_frame,
            text="📊 Generate Report",
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=8,
            command=self.generate_date_range_report
        ).pack(side=tk.LEFT, padx=20)
        
        # Report display
        self.range_report_text = tk.Text(self.range_tab, font=("Courier", 10), wrap=tk.WORD)
        self.range_report_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        scrollbar = tk.Scrollbar(self.range_report_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.range_report_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.range_report_text.yview)
    
    def create_product_performance_tab(self):
        """Create product performance tab"""
        tk.Label(
            self.product_tab,
            text="Product Sales Performance",
            font=("Arial", 14, "bold")
        ).pack(pady=15)
        
        # Performance list
        columns = ('product', 'quality', 'qty_kg', 'qty_bags', 'revenue', 'transactions')
        self.product_tree = ttk.Treeview(self.product_tab, columns=columns, show='headings', height=20)
        
        self.product_tree.heading('product', text='Product Name')
        self.product_tree.heading('quality', text='Quality')
        self.product_tree.heading('qty_kg', text='Total KG Sold')
        self.product_tree.heading('qty_bags', text='Total Bags Sold')
        self.product_tree.heading('revenue', text='Total Revenue')
        self.product_tree.heading('transactions', text='# Transactions')
        
        scrollbar = ttk.Scrollbar(self.product_tab, orient=tk.VERTICAL, command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=scrollbar.set)
        
        self.product_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 20))
        
        # Buttons
        btn_frame = tk.Frame(self.product_tab)
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="🔄 Refresh",
            font=("Arial", 11),
            bg="#95a5a6",
            fg="white",
            padx=20,
            pady=8,
            command=self.load_product_performance
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="📥 Export to CSV",
            font=("Arial", 11),
            bg="#3498db",
            fg="white",
            padx=20,
            pady=8,
            command=lambda: self.export_to_csv('product_performance')
        ).pack(side=tk.LEFT, padx=5)
        
        # Load initial data
        self.load_product_performance()
    
    def load_today_summary(self):
        """Load today's summary data"""
        summary = db.get_today_summary()
        
        if summary:
            self.today_sales_label.config(text=f"₹{summary['total_sales']:.2f}")
            self.today_trans_label.config(text=str(summary['total_transactions']))
            self.today_cash_label.config(text=f"₹{summary['cash_sales']:.2f}")
            self.today_credit_label.config(text=f"₹{summary['credit_sales']:.2f}")
        
        # Load today's sales
        sales = db.fetch_all(
            """SELECT s.sale_number, s.sale_date, u.full_name as cashier,
                      s.customer_name, s.final_amount, s.payment_method
               FROM sales s
               JOIN users u ON s.cashier_id = u.id
               WHERE DATE(s.sale_date) = DATE('now') AND s.is_voided = 0
               ORDER BY s.sale_date DESC""")
        
        # Clear and populate tree
        for item in self.today_sales_tree.get_children():
            self.today_sales_tree.delete(item)
        
        for sale in sales:
            time_str = datetime.strptime(sale['sale_date'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S')
            self.today_sales_tree.insert('', tk.END, values=(
                sale['sale_number'],
                time_str,
                sale['cashier'],
                sale['customer_name'] or 'Walk-in',
                f"₹{sale['final_amount']:.2f}",
                sale['payment_method'].upper()
            ))
    
    def load_sales_history(self):
        """Load all sales history"""
        sales = db.fetch_all(
            """SELECT s.id, s.sale_number, s.sale_date, u.full_name as cashier,
                      s.customer_name, s.total_amount, s.discount_amount,
                      s.final_amount, s.payment_method
               FROM sales s
               JOIN users u ON s.cashier_id = u.id
               WHERE s.is_voided = 0
               ORDER BY s.sale_date DESC
               LIMIT 500""")
        
        # Clear and populate tree
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        
        for sale in sales:
            self.sales_tree.insert('', tk.END, values=(
                sale['id'],
                sale['sale_number'],
                sale['sale_date'],
                sale['cashier'],
                sale['customer_name'] or 'Walk-in',
                f"₹{sale['total_amount']:.2f}",
                f"₹{sale['discount_amount']:.2f}",
                f"₹{sale['final_amount']:.2f}",
                sale['payment_method'].upper()
            ))
    
    def search_sales(self):
        """Search sales by sale number or customer name"""
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            self.load_sales_history()
            return
        
        sales = db.fetch_all(
            """SELECT s.id, s.sale_number, s.sale_date, u.full_name as cashier,
                      s.customer_name, s.total_amount, s.discount_amount,
                      s.final_amount, s.payment_method
               FROM sales s
               JOIN users u ON s.cashier_id = u.id
               WHERE s.is_voided = 0 AND (
                   s.sale_number LIKE ? OR
                   s.customer_name LIKE ?
               )
               ORDER BY s.sale_date DESC""",
            (f'%{search_term}%', f'%{search_term}%'))
        
        # Clear and populate tree
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        
        for sale in sales:
            self.sales_tree.insert('', tk.END, values=(
                sale['id'],
                sale['sale_number'],
                sale['sale_date'],
                sale['cashier'],
                sale['customer_name'] or 'Walk-in',
                f"₹{sale['total_amount']:.2f}",
                f"₹{sale['discount_amount']:.2f}",
                f"₹{sale['final_amount']:.2f}",
                sale['payment_method'].upper()
            ))
    
    def view_sale_details(self, event):
        """View detailed sale information"""
        selection = self.sales_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a sale to view")
            return
        
        sale_id = self.sales_tree.item(selection[0])['values'][0]
        sale_details = db.get_sale_details(sale_id)
        
        if not sale_details:
            messagebox.showerror("Error", "Sale not found")
            return
        
        # Create details window
        details_window = tk.Toplevel(self.window)
        details_window.title(f"Sale Details - {sale_details['sale']['sale_number']}")
        details_window.geometry("500x600")
        
        details_text = tk.Text(details_window, font=("Courier", 10), wrap=tk.WORD)
        details_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Build details content
        sale = sale_details['sale']
        items = sale_details['items']
        
        details = "="*50 + "\n"
        details += "           SALE DETAILS\n"
        details += "="*50 + "\n\n"
        details += f"Sale Number: {sale['sale_number']}\n"
        details += f"Date: {sale['sale_date']}\n"
        details += f"Cashier: {sale['cashier_name']}\n"
        details += f"Customer: {sale['customer_name'] or 'Walk-in'}\n"
        details += f"Payment Method: {sale['payment_method'].upper()}\n"
        details += f"Payment Status: {sale['payment_status'].upper()}\n\n"
        
        details += "-"*50 + "\n"
        details += "ITEMS:\n"
        details += "-"*50 + "\n\n"
        
        for item in items:
            details += f"{item['product_name']}\n"
            if item['sale_type'] == 'by_kg':
                details += f"  {item['quantity_kg']:.2f}kg x ₹{item['price_per_unit']:.2f}/kg"
            else:
                details += f"  {item['quantity_bags']} bags x ₹{item['price_per_unit']:.2f}"
            details += f" = ₹{item['subtotal']:.2f}\n\n"
        
        details += "-"*50 + "\n"
        details += f"Subtotal: ₹{sale['total_amount']:.2f}\n"
        
        if sale['discount_amount'] > 0:
            details += f"Discount: -₹{sale['discount_amount']:.2f}\n"
            if sale['discount_reason']:
                details += f"Reason: {sale['discount_reason']}\n"
        
        details += f"\nTOTAL: ₹{sale['final_amount']:.2f}\n"
        details += "="*50 + "\n"
        
        details_text.insert('1.0', details)
        details_text.config(state=tk.DISABLED)
        
        tk.Button(
            details_window,
            text="Close",
            font=("Arial", 11),
            command=details_window.destroy
        ).pack(pady=10)
    
    def generate_date_range_report(self):
        """Generate report for date range"""
        try:
            from_date = self.from_date_entry.get()
            to_date = self.to_date_entry.get()
            
            # Validate dates
            datetime.strptime(from_date, '%Y-%m-%d')
            datetime.strptime(to_date, '%Y-%m-%d')
            
            # Get data
            summary = db.fetch_one(
                """SELECT 
                    COUNT(*) as total_transactions,
                    COALESCE(SUM(final_amount), 0) as total_sales,
                    COALESCE(SUM(discount_amount), 0) as total_discount,
                    COALESCE(SUM(CASE WHEN payment_method = 'cash' THEN final_amount ELSE 0 END), 0) as cash_sales,
                    COALESCE(SUM(CASE WHEN payment_method = 'credit' THEN final_amount ELSE 0 END), 0) as credit_sales
                   FROM sales
                   WHERE DATE(sale_date) BETWEEN ? AND ? AND is_voided = 0""",
                (from_date, to_date))
            
            # Build report
            report = "="*60 + "\n"
            report += f"     SALES REPORT: {from_date} to {to_date}\n"
            report += "="*60 + "\n\n"
            
            report += f"Total Transactions: {summary['total_transactions']}\n"
            report += f"Total Sales: ₹{summary['total_sales']:.2f}\n"
            report += f"Total Discount: ₹{summary['total_discount']:.2f}\n"
            report += f"Cash Sales: ₹{summary['cash_sales']:.2f}\n"
            report += f"Credit Sales: ₹{summary['credit_sales']:.2f}\n\n"
            
            report += "-"*60 + "\n"
            report += "DAILY BREAKDOWN:\n"
            report += "-"*60 + "\n\n"
            
            daily = db.fetch_all(
                """SELECT 
                    DATE(sale_date) as date,
                    COUNT(*) as transactions,
                    SUM(final_amount) as sales
                   FROM sales
                   WHERE DATE(sale_date) BETWEEN ? AND ? AND is_voided = 0
                   GROUP BY DATE(sale_date)
                   ORDER BY date""",
                (from_date, to_date))
            
            for day in daily:
                report += f"{day['date']}: {day['transactions']} transactions, ₹{day['sales']:.2f}\n"
            
            report += "\n" + "="*60 + "\n"
            
            # Display report
            self.range_report_text.delete('1.0', tk.END)
            self.range_report_text.insert('1.0', report)
            
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
    
    def load_product_performance(self):
        """Load product performance data"""
        performance = db.fetch_all(
            """SELECT 
                p.name,
                p.quality,
                COALESCE(SUM(si.quantity_kg), 0) as total_kg,
                COALESCE(SUM(si.quantity_bags), 0) as total_bags,
                COALESCE(SUM(si.subtotal), 0) as revenue,
                COUNT(DISTINCT si.sale_id) as transactions
               FROM products p
               LEFT JOIN sale_items si ON p.id = si.product_id
               LEFT JOIN sales s ON si.sale_id = s.id AND s.is_voided = 0
               WHERE p.is_active = 1
               GROUP BY p.id
               ORDER BY revenue DESC""")
        
        # Clear and populate tree
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        for prod in performance:
            self.product_tree.insert('', tk.END, values=(
                prod['name'],
                prod['quality'].title(),
                f"{prod['total_kg']:.2f}",
                prod['total_bags'],
                f"₹{prod['revenue']:.2f}",
                prod['transactions']
            ))
    
    def export_to_csv(self, report_type):
        """Export report data to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                if report_type == 'today':
                    writer.writerow(['Sale Number', 'Time', 'Cashier', 'Customer', 'Amount', 'Payment'])
                    for child in self.today_sales_tree.get_children():
                        writer.writerow(self.today_sales_tree.item(child)['values'])
                
                elif report_type == 'all_sales':
                    writer.writerow(['ID', 'Sale Number', 'Date', 'Cashier', 'Customer', 'Amount', 'Discount', 'Final Amount', 'Payment'])
                    for child in self.sales_tree.get_children():
                        writer.writerow(self.sales_tree.item(child)['values'])
                
                elif report_type == 'product_performance':
                    writer.writerow(['Product', 'Quality', 'Total KG', 'Total Bags', 'Revenue', 'Transactions'])
                    for child in self.product_tree.get_children():
                        writer.writerow(self.product_tree.item(child)['values'])
            
            messagebox.showinfo("Success", f"Data exported successfully to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")