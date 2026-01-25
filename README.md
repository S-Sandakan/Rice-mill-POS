# Rice-mill-POS
Rice Mill POS System - Offline Point of Sale
Complete offline POS system for small rice mill businesses built with Python and SQLite.

Features
✅ Offline-First Design - Works completely without internet ✅ User Management - Admin and Cashier roles ✅ Product Management - Rice types with quality levels ✅ Stock Management - Track inventory in kg and bags ✅ Sales Processing - Cash and credit sales ✅ Receipt Generation - Printable receipts ✅ Reports & Analytics - Daily, date range, and product performance reports ✅ Data Export - Export to CSV for backup

System Requirements
Operating System: Windows 7/10/11 or Linux
Python: 3.7 or higher
RAM: Minimum 2GB (4GB recommended)
Storage: 500MB free space
Display: 1024x768 minimum resolution
Installation
Step 1: Install Python
Windows:

Download Python from https://www.python.org/downloads/
Run installer and check "Add Python to PATH"
Complete installation
Linux:

bash
sudo apt update
sudo apt install python3 python3-pip python3-tk
Step 2: Download Application Files
Create a folder for the application:

RiceMillPOS/
├── schema.sql
├── database.py
├── main.py
├── stock_manager.py
├── product_manager.py
├── reports.py
└── README.md
Step 3: Install Dependencies (if needed)
The system uses only Python standard library modules:

tkinter (built-in with Python)
sqlite3 (built-in with Python)
If tkinter is not available:

bash
# Linux
sudo apt-get install python3-tk

# The system should work without additional installations
Step 4: Initialize Database
Run the database initialization:

Windows:

cmd
python database.py
Linux:

bash
python3 database.py
This will create ricemill_pos.db with sample data.

Step 5: Run Application
Windows:

cmd
python main.py
Linux:

bash
python3 main.py
Default Login Credentials
Username: admin
Password: admin123
Role: Administrator
⚠️ Important: Change the default password after first login!

File Structure
RiceMillPOS/
├── ricemill_pos.db          # SQLite database (auto-created)
├── schema.sql               # Database schema
├── database.py              # Database operations
├── main.py                  # Main application
├── stock_manager.py         # Stock management module
├── product_manager.py       # Product management module
├── reports.py               # Reports and analytics
└── backups/                 # Automatic backups (optional)
Usage Guide
1. Login
Enter username and password
Click Login or press Enter
2. Making a Sale
Select product from left panel
Click "Add to Cart" or double-click
Choose sale type (by kg or by bag)
Enter quantity
Click "Add to Cart"
Repeat for additional items
Apply discount if needed (Admin only)
Click "Cash Sale" or "Credit Sale"
View/print receipt
3. Managing Stock (Admin)
Menu → Products → Manage Stock
Select product
Choose:
Restock: Add new inventory
Adjust Stock: Correct errors
Enter quantities and notes
Confirm changes
4. Adding Products (Admin)
Menu → Products → Add Product
Fill in details:
Product code (unique)
Product name
Quality level
Price per kg
Bag size and price (optional)
Click "Save Product"
5. Viewing Reports
Menu → Reports → Sales Reports
Choose tab:
Today's Summary
Sales History
Date Range Report
Product Performance
Export to CSV if needed
Keyboard Shortcuts
F1: New Sale (Clear Cart)
Enter: Login / Confirm dialogs
Double-click: Add product to cart
Data Backup
Manual Backup
Simply copy the database file:

RiceMillPOS/ricemill_pos.db
Save to USB drive or external storage regularly.

Recommended Backup Schedule
Daily: At end of business day
Weekly: To external storage
Monthly: Archive copy
Troubleshooting
Application Won't Start
Error: No module named 'tkinter'

bash
# Linux
sudo apt-get install python3-tk
Error: Database locked

Close all instances of the application
Restart the application
Database Issues
Reset Database:

bash
# Backup current database first!
mv ricemill_pos.db ricemill_pos.db.backup

# Run initialization
python database.py
Display Issues
Window too small/large:

Edit main.py, line: self.root.geometry("1200x700")
Adjust dimensions as needed
Adding New Users
Currently, users can only be added via database:

python
# In Python console
from database import db
db.create_user(
    username='cashier1',
    password='password123',
    role='cashier',
    full_name='John Doe'
)
Or use SQL directly:

sql
INSERT INTO users (username, password_hash, role, full_name) 
VALUES ('cashier1', 'password123', 'cashier', 'John Doe');
Sample Data
The system comes with sample rice products:

Basmati Rice (Premium)
Sona Masoori (Standard)
IR64 (Economic)
Ponni Rice (Standard)
You can modify or delete these and add your own products.

Export Data
Export Sales to CSV
Menu → Reports → Sales Reports
Select appropriate tab
Click "Export to CSV"
Choose location and filename
Open in Excel/LibreOffice
Export Stock Status
Menu → Reports → Sales Reports
Product Performance tab
Click "Export to CSV"
Security Recommendations
Change default password immediately
Backup database regularly
Limit admin access - only trusted users
Store database securely - encrypted drive recommended
Use strong passwords for all users
Performance Optimization
For Slower Computers
Edit database.py to limit query results:

python
# Line ~450 in reports.py
LIMIT 500  # Reduce to 100 or 50
Database Maintenance
Run periodically:

sql
VACUUM;
ANALYZE;
Or in Python:

python
from database import db
db.execute_query("VACUUM")
db.execute_query("ANALYZE")
Customization
Change Currency Symbol
Edit schema.sql:

sql
INSERT INTO settings (key, value) VALUES 
('currency_symbol', '₹');  -- Change to $, £, etc.
Change Receipt Header
Edit main.py, function show_receipt():

python
receipt = "="*40 + "\n"
receipt += "    YOUR BUSINESS NAME HERE\n"  # Customize
receipt += "      Address Line 1\n"          # Customize
receipt += "      Phone: 123-456-7890\n"     # Customize
Add Business Logo
Replace header in main.py:

python
# Load image (requires PIL/Pillow)
from PIL import Image, ImageTk
logo = ImageTk.PhotoImage(Image.open("logo.png"))
logo_label = tk.Label(header_frame, image=logo, bg="#34495e")
logo_label.pack(side=tk.LEFT)
Extending the System
Add New Features
The modular design allows easy extensions:

SMS Notifications - Add to checkout() function
Barcode Scanner - Integrate in add_to_cart()
Thermal Printer - Add printer module to show_receipt()
Multi-language - Add language files and translation function
Database Schema Extensions
You can add new tables as needed:

sql
-- Example: Customer database
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT,
    address TEXT,
    credit_limit REAL DEFAULT 0
);
Support & Contact
For issues or questions:

Check troubleshooting section above
Review error messages carefully
Check database file exists and is not corrupted
License
This system is provided as-is for small business use.
Feel free to modify and customize for your needs.

Version History
v1.0 (2025-01-25)

Initial release
Core POS functionality
Stock management
Reports and analytics
Offline-first design
Quick Start Checklist
 Install Python 3.7+
 Download all application files
 Run python database.py to initialize
 Run python main.py to start
 Login with admin/admin123
 Change default password
 Add your products
 Add initial stock
 Create cashier users
 Make test sale
 Set up backup schedule
 Begin daily operations
System is ready for use! 🎉

