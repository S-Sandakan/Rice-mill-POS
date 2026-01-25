"""
Rice Mill POS System - Database Module
Handles all database operations and initialization
"""

import sqlite3
import os
import hashlib
from datetime import datetime
from typing import Optional, List, Dict, Any

class Database:
    def __init__(self, db_path: str = "ricemill_pos.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.connection = None
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get or create database connection"""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def init_database(self):
        """Initialize database with schema"""
        # Read schema from file or use embedded schema
        schema_file = "schema.sql"
        
        if os.path.exists(schema_file):
            with open(schema_file, 'r') as f:
                schema = f.read()
        else:
            schema = self.get_embedded_schema()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.executescript(schema)
        conn.commit()
        print("Database initialized successfully")
    
    def get_embedded_schema(self) -> str:
        """Returns embedded database schema"""
        return """
        -- Embedded schema (copy from schema.sql)
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT CHECK(role IN ('admin', 'cashier')) NOT NULL,
            full_name TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            quality TEXT NOT NULL,
            price_per_kg REAL NOT NULL,
            bag_size_kg REAL,
            price_per_bag REAL,
            description TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity_kg REAL NOT NULL DEFAULT 0,
            quantity_bags INTEGER NOT NULL DEFAULT 0,
            min_stock_kg REAL DEFAULT 50,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_by INTEGER,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY (updated_by) REFERENCES users(id)
        );
        
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_number TEXT UNIQUE NOT NULL,
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cashier_id INTEGER NOT NULL,
            customer_name TEXT,
            customer_phone TEXT,
            total_amount REAL NOT NULL,
            discount_amount REAL DEFAULT 0,
            discount_reason TEXT,
            final_amount REAL NOT NULL,
            payment_method TEXT DEFAULT 'cash',
            payment_status TEXT DEFAULT 'paid',
            notes TEXT,
            is_voided INTEGER DEFAULT 0,
            voided_by INTEGER,
            voided_at TIMESTAMP,
            void_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cashier_id) REFERENCES users(id),
            FOREIGN KEY (voided_by) REFERENCES users(id)
        );
        
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            sale_type TEXT CHECK(sale_type IN ('by_kg', 'by_bag')) NOT NULL,
            quantity_kg REAL,
            quantity_bags INTEGER,
            price_per_unit REAL NOT NULL,
            subtotal REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id)
        );
        
        CREATE TABLE IF NOT EXISTS stock_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            transaction_type TEXT CHECK(transaction_type IN ('sale', 'adjustment', 'restock')) NOT NULL,
            quantity_kg_change REAL,
            quantity_bags_change INTEGER,
            reference_id INTEGER,
            reference_type TEXT,
            performed_by INTEGER NOT NULL,
            notes TEXT,
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (performed_by) REFERENCES users(id)
        );
        
        CREATE TABLE IF NOT EXISTS daily_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            summary_date DATE UNIQUE NOT NULL,
            total_sales REAL DEFAULT 0,
            total_discount REAL DEFAULT 0,
            total_transactions INTEGER DEFAULT 0,
            cash_sales REAL DEFAULT 0,
            credit_sales REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Insert default admin user
        INSERT OR IGNORE INTO users (username, password_hash, role, full_name) 
        VALUES ('admin', 'admin123', 'admin', 'Administrator');
        
        -- Insert sample products
        INSERT OR IGNORE INTO products (product_code, name, quality, price_per_kg, bag_size_kg, price_per_bag, description) 
        VALUES 
        ('RICE001', 'Basmati Rice', 'premium', 65.00, 25.0, 1625.00, 'Premium quality Basmati rice'),
        ('RICE002', 'Sona Masoori', 'standard', 45.00, 25.0, 1125.00, 'Standard quality Sona Masoori'),
        ('RICE003', 'IR64', 'economic', 38.00, 50.0, 1900.00, 'Economic quality IR64 rice'),
        ('RICE004', 'Ponni Rice', 'standard', 42.00, 25.0, 1050.00, 'Standard quality Ponni rice');
        
        -- Insert initial stock
        INSERT OR IGNORE INTO stock (product_id, quantity_kg, quantity_bags, min_stock_kg) 
        VALUES 
        (1, 500.0, 20, 100.0),
        (2, 750.0, 30, 150.0),
        (3, 1000.0, 20, 200.0),
        (4, 625.0, 25, 125.0);
        """
    
    def execute_query(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query and return cursor"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """Fetch single row"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
    
    def fetch_all(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Fetch all rows"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    # User Authentication Methods
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return user data"""
        user = self.fetch_one(
            "SELECT * FROM users WHERE username = ? AND is_active = 1",
            (username,)
        )
        
        if user and user['password_hash'] == password:
            return {
                'id': user['id'],
                'username': user['username'],
                'role': user['role'],
                'full_name': user['full_name']
            }
        return None
    
    def create_user(self, username: str, password: str, role: str, full_name: str) -> int:
        """Create new user"""
        cursor = self.execute_query(
            """INSERT INTO users (username, password_hash, role, full_name) 
               VALUES (?, ?, ?, ?)""",
            (username, password, role, full_name)
        )
        return cursor.lastrowid
    
    # Product Methods
    def get_all_products(self, active_only: bool = True) -> List[sqlite3.Row]:
        """Get all products"""
        query = "SELECT * FROM products"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY name"
        return self.fetch_all(query)
    
    def get_product_by_id(self, product_id: int) -> Optional[sqlite3.Row]:
        """Get product by ID"""
        return self.fetch_one("SELECT * FROM products WHERE id = ?", (product_id,))
    
    def add_product(self, product_code: str, name: str, quality: str, 
                   price_per_kg: float, bag_size_kg: float = None, 
                   price_per_bag: float = None, description: str = None) -> int:
        """Add new product"""
        cursor = self.execute_query(
            """INSERT INTO products (product_code, name, quality, price_per_kg, 
               bag_size_kg, price_per_bag, description) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (product_code, name, quality, price_per_kg, bag_size_kg, price_per_bag, description)
        )
        
        # Initialize stock for new product
        self.execute_query(
            "INSERT INTO stock (product_id, quantity_kg, quantity_bags) VALUES (?, 0, 0)",
            (cursor.lastrowid,)
        )
        
        return cursor.lastrowid
    
    def update_product(self, product_id: int, **kwargs) -> bool:
        """Update product details"""
        allowed_fields = ['name', 'quality', 'price_per_kg', 'bag_size_kg', 
                         'price_per_bag', 'description', 'is_active']
        
        updates = []
        values = []
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                values.append(value)
        
        if not updates:
            return False
        
        values.append(product_id)
        query = f"UPDATE products SET {', '.join(updates)} WHERE id = ?"
        self.execute_query(query, tuple(values))
        return True
    
    # Stock Methods
    def get_stock_by_product(self, product_id: int) -> Optional[sqlite3.Row]:
        """Get stock for a product"""
        return self.fetch_one("SELECT * FROM stock WHERE product_id = ?", (product_id,))
    
    def get_all_stock_status(self) -> List[sqlite3.Row]:
        """Get stock status for all products"""
        query = """
        SELECT 
            p.id, p.product_code, p.name, p.quality,
            p.price_per_kg, p.price_per_bag,
            s.quantity_kg, s.quantity_bags, s.min_stock_kg,
            CASE 
                WHEN s.quantity_kg < s.min_stock_kg THEN 'Low Stock'
                WHEN s.quantity_kg = 0 THEN 'Out of Stock'
                ELSE 'Available'
            END AS stock_status,
            s.last_updated
        FROM products p
        LEFT JOIN stock s ON p.id = s.product_id
        WHERE p.is_active = 1
        ORDER BY p.name
        """
        return self.fetch_all(query)
    
    def update_stock(self, product_id: int, quantity_kg_change: float, 
                    quantity_bags_change: int, user_id: int, 
                    transaction_type: str, notes: str = None) -> bool:
        """Update stock levels"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Update stock
            cursor.execute(
                """UPDATE stock 
                   SET quantity_kg = quantity_kg + ?,
                       quantity_bags = quantity_bags + ?,
                       updated_by = ?
                   WHERE product_id = ?""",
                (quantity_kg_change, quantity_bags_change, user_id, product_id)
            )
            
            # Log transaction
            cursor.execute(
                """INSERT INTO stock_transactions 
                   (product_id, transaction_type, quantity_kg_change, 
                    quantity_bags_change, performed_by, notes)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (product_id, transaction_type, quantity_kg_change, 
                 quantity_bags_change, user_id, notes)
            )
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Stock update error: {e}")
            return False
    
    # Sales Methods
    def generate_sale_number(self) -> str:
        """Generate unique sale number"""
        today = datetime.now().strftime('%Y%m%d')
        
        count = self.fetch_one(
            "SELECT COUNT(*) as count FROM sales WHERE DATE(sale_date) = DATE('now')"
        )
        
        return f"{today}-{str(count['count'] + 1).zfill(4)}"
    
    def create_sale(self, cashier_id: int, items: List[Dict], 
                   discount_amount: float = 0, discount_reason: str = None,
                   payment_method: str = 'cash', customer_name: str = None,
                   customer_phone: str = None, notes: str = None) -> Optional[int]:
        """Create a new sale with items"""
        conn = self.get_connection()
        
        try:
            cursor = conn.cursor()
            
            # Calculate totals
            total_amount = sum(item['subtotal'] for item in items)
            final_amount = total_amount - discount_amount
            
            # Generate sale number
            sale_number = self.generate_sale_number()
            
            # Insert sale record
            cursor.execute(
                """INSERT INTO sales 
                   (sale_number, cashier_id, customer_name, customer_phone,
                    total_amount, discount_amount, discount_reason, final_amount,
                    payment_method)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (sale_number, cashier_id, customer_name, customer_phone,
                 total_amount, discount_amount, discount_reason, final_amount,
                 payment_method)
            )
            
            sale_id = cursor.lastrowid
            
            # Insert sale items and update stock
            for item in items:
                # Insert sale item
                cursor.execute(
                    """INSERT INTO sale_items 
                       (sale_id, product_id, product_name, sale_type,
                        quantity_kg, quantity_bags, price_per_unit, subtotal)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (sale_id, item['product_id'], item['product_name'], 
                     item['sale_type'], item.get('quantity_kg'), 
                     item.get('quantity_bags'), item['price_per_unit'], 
                     item['subtotal'])
                )
                
                # Update stock
                qty_kg = -(item.get('quantity_kg') or 0)
                qty_bags = -(item.get('quantity_bags') or 0)
                
                cursor.execute(
                    """UPDATE stock 
                       SET quantity_kg = quantity_kg + ?,
                           quantity_bags = quantity_bags + ?,
                           updated_by = ?
                       WHERE product_id = ?""",
                    (qty_kg, qty_bags, cashier_id, item['product_id'])
                )
                
                # Log stock transaction
                cursor.execute(
                    """INSERT INTO stock_transactions 
                       (product_id, transaction_type, quantity_kg_change,
                        quantity_bags_change, reference_id, reference_type,
                        performed_by, notes)
                       VALUES (?, 'sale', ?, ?, ?, 'sale', ?, ?)""",
                    (item['product_id'], qty_kg, qty_bags, sale_id, 
                     cashier_id, f"Sale #{sale_number}")
                )
            
            conn.commit()
            return sale_id
            
        except Exception as e:
            conn.rollback()
            print(f"Sale creation error: {e}")
            return None
    
    def get_today_summary(self) -> Optional[sqlite3.Row]:
        """Get today's sales summary"""
        query = """
        SELECT 
            COUNT(*) as total_transactions,
            COALESCE(SUM(final_amount), 0) as total_sales,
            COALESCE(SUM(discount_amount), 0) as total_discount,
            COALESCE(SUM(CASE WHEN payment_method = 'cash' THEN final_amount ELSE 0 END), 0) as cash_sales,
            COALESCE(SUM(CASE WHEN payment_method = 'credit' THEN final_amount ELSE 0 END), 0) as credit_sales
        FROM sales
        WHERE DATE(sale_date) = DATE('now') AND is_voided = 0
        """
        return self.fetch_one(query)
    
    def get_recent_sales(self, limit: int = 10) -> List[sqlite3.Row]:
        """Get recent sales"""
        query = """
        SELECT 
            s.id, s.sale_number, s.sale_date, u.full_name as cashier_name,
            s.customer_name, s.final_amount, s.payment_method, s.is_voided
        FROM sales s
        JOIN users u ON s.cashier_id = u.id
        ORDER BY s.sale_date DESC
        LIMIT ?
        """
        return self.fetch_all(query, (limit,))
    
    def get_sale_details(self, sale_id: int) -> Dict[str, Any]:
        """Get complete sale details with items"""
        sale = self.fetch_one(
            """SELECT s.*, u.full_name as cashier_name
               FROM sales s
               JOIN users u ON s.cashier_id = u.id
               WHERE s.id = ?""",
            (sale_id,)
        )
        
        if not sale:
            return None
        
        items = self.fetch_all(
            "SELECT * FROM sale_items WHERE sale_id = ?",
            (sale_id,)
        )
        
        return {
            'sale': dict(sale),
            'items': [dict(item) for item in items]
        }


# Initialize database instance
db = Database()

if __name__ == "__main__":
    print("Database initialized successfully!")
    print(f"Database file: {db.db_path}")