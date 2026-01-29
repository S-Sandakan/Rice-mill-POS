"""
Rice Mill POS System - Backup Utility
Automated database backup tool
"""

import os
import shutil
import sqlite3
from datetime import datetime
import argparse


class BackupManager:
    """Manages database backups"""
    
    def __init__(self, db_path="ricemill_pos.db", backup_dir="backups"):
        self.db_path = db_path
        self.backup_dir = backup_dir
        
        # Create backup directory if it doesn't exist
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
    
    def create_backup(self):
        """Create a backup of the database"""
        if not os.path.exists(self.db_path):
            print(f"ERROR: Database file '{self.db_path}' not found!")
            return False
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"ricemill_pos_backup_{timestamp}.db"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            # Copy database file
            shutil.copy2(self.db_path, backup_path)
            
            # Get file size
            size = os.path.getsize(backup_path)
            size_mb = size / (1024 * 1024)
            
            print(f"✓ Backup created successfully!")
            print(f"  File: {backup_path}")
            print(f"  Size: {size_mb:.2f} MB")
            print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to create backup - {str(e)}")
            return False
    
    def list_backups(self):
        """List all available backups"""
        if not os.path.exists(self.backup_dir):
            print("No backups directory found")
            return []
        
        backups = []
        for filename in os.listdir(self.backup_dir):
            if filename.endswith('.db'):
                filepath = os.path.join(self.backup_dir, filename)
                size = os.path.getsize(filepath)
                mtime = os.path.getmtime(filepath)
                
                backups.append({
                    'filename': filename,
                    'path': filepath,
                    'size': size,
                    'modified': datetime.fromtimestamp(mtime)
                })
        
        # Sort by modification time (newest first)
        backups.sort(key=lambda x: x['modified'], reverse=True)
        
        if backups:
            print("\nAvailable backups:")
            print("-" * 80)
            print(f"{'#':<4} {'Filename':<40} {'Size':<12} {'Date':<20}")
            print("-" * 80)
            
            for i, backup in enumerate(backups, 1):
                size_mb = backup['size'] / (1024 * 1024)
                date_str = backup['modified'].strftime('%Y-%m-%d %H:%M:%S')
                print(f"{i:<4} {backup['filename']:<40} {size_mb:>8.2f} MB {date_str}")
            
            print("-" * 80)
        else:
            print("No backups found")
        
        return backups
    
    def restore_backup(self, backup_path):
        """Restore database from backup"""
        if not os.path.exists(backup_path):
            print(f"ERROR: Backup file '{backup_path}' not found!")
            return False
        
        try:
            # Create a backup of current database first
            if os.path.exists(self.db_path):
                safety_backup = f"{self.db_path}.before_restore"
                shutil.copy2(self.db_path, safety_backup)
                print(f"Current database backed up to: {safety_backup}")
            
            # Restore from backup
            shutil.copy2(backup_path, self.db_path)
            
            print(f"✓ Database restored successfully from: {backup_path}")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to restore backup - {str(e)}")
            return False
    
    def clean_old_backups(self, keep_count=30):
        """Remove old backups, keeping only the most recent ones"""
        backups = self.list_backups()
        
        if len(backups) <= keep_count:
            print(f"Only {len(backups)} backups found. No cleanup needed.")
            return
        
        # Remove old backups
        to_remove = backups[keep_count:]
        
        print(f"\nRemoving {len(to_remove)} old backup(s)...")
        
        for backup in to_remove:
            try:
                os.remove(backup['path'])
                print(f"  Removed: {backup['filename']}")
            except Exception as e:
                print(f"  ERROR removing {backup['filename']}: {str(e)}")
        
        print(f"✓ Cleanup complete. {keep_count} most recent backups retained.")
    
    def export_to_sql(self, output_file=None):
        """Export database to SQL dump file"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"ricemill_pos_dump_{timestamp}.sql"
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                for line in conn.iterdump():
                    f.write(f'{line}\n')
            
            conn.close()
            
            size = os.path.getsize(output_file)
            size_kb = size / 1024
            
            print(f"✓ SQL dump created successfully!")
            print(f"  File: {output_file}")
            print(f"  Size: {size_kb:.2f} KB")
            
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to create SQL dump - {str(e)}")
            return False
    
    def get_database_info(self):
        """Display database information"""
        if not os.path.exists(self.db_path):
            print("Database not found")
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            print("\n" + "="*60)
            print("DATABASE INFORMATION")
            print("="*60)
            
            # Database file info
            size = os.path.getsize(self.db_path)
            size_mb = size / (1024 * 1024)
            mtime = datetime.fromtimestamp(os.path.getmtime(self.db_path))
            
            print(f"File: {self.db_path}")
            print(f"Size: {size_mb:.2f} MB")
            print(f"Last Modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
            # Table statistics
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = cursor.fetchall()
            
            print("Table Statistics:")
            print("-" * 60)
            print(f"{'Table Name':<30} {'Row Count':>15}")
            print("-" * 60)
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"{table_name:<30} {count:>15,}")
            
            print("-" * 60)
            
            # Additional info
            cursor.execute("SELECT COUNT(*) FROM sales WHERE DATE(sale_date) = DATE('now')")
            today_sales = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM products WHERE is_active = 1")
            active_products = cursor.fetchone()[0]
            
            print()
            print(f"Active Products: {active_products}")
            print(f"Sales Today: {today_sales}")
            print("="*60)
            
            conn.close()
            
        except Exception as e:
            print(f"ERROR: {str(e)}")


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='Rice Mill POS Database Backup Utility')
    parser.add_argument('--backup', action='store_true', help='Create a new backup')
    parser.add_argument('--list', action='store_true', help='List all backups')
    parser.add_argument('--restore', metavar='BACKUP_FILE', help='Restore from backup file')
    parser.add_argument('--clean', type=int, metavar='KEEP_COUNT', 
                       help='Clean old backups, keeping specified count')
    parser.add_argument('--export-sql', action='store_true', help='Export database to SQL dump')
    parser.add_argument('--info', action='store_true', help='Display database information')
    parser.add_argument('--db', default='ricemill_pos.db', help='Database file path')
    parser.add_argument('--backup-dir', default='backups', help='Backup directory path')
    
    args = parser.parse_args()
    
    # Create backup manager
    manager = BackupManager(db_path=args.db, backup_dir=args.backup_dir)
    
    # Execute requested action
    if args.backup:
        manager.create_backup()
    
    elif args.list:
        manager.list_backups()
    
    elif args.restore:
        manager.restore_backup(args.restore)
    
    elif args.clean:
        manager.clean_old_backups(keep_count=args.clean)
    
    elif args.export_sql:
        manager.export_to_sql()
    
    elif args.info:
        manager.get_database_info()
    
    else:
        # Interactive mode
        print("="*60)
        print("Rice Mill POS - Backup Utility")
        print("="*60)
        print()
        print("1. Create new backup")
        print("2. List all backups")
        print("3. Restore from backup")
        print("4. Clean old backups")
        print("5. Export to SQL dump")
        print("6. Database information")
        print("7. Exit")
        print()
        
        choice = input("Select option (1-7): ").strip()
        
        if choice == '1':
            manager.create_backup()
        
        elif choice == '2':
            manager.list_backups()
        
        elif choice == '3':
            backups = manager.list_backups()
            if backups:
                try:
                    num = int(input("\nEnter backup number to restore: "))
                    if 1 <= num <= len(backups):
                        confirm = input(f"Restore from '{backups[num-1]['filename']}'? (yes/no): ")
                        if confirm.lower() == 'yes':
                            manager.restore_backup(backups[num-1]['path'])
                    else:
                        print("Invalid backup number")
                except ValueError:
                    print("Invalid input")
        
        elif choice == '4':
            try:
                keep = int(input("How many recent backups to keep? (default 30): ") or "30")
                manager.clean_old_backups(keep_count=keep)
            except ValueError:
                print("Invalid input")
        
        elif choice == '5':
            manager.export_to_sql()
        
        elif choice == '6':
            manager.get_database_info()
        
        elif choice == '7':
            print("Exiting...")
        
        else:
            print("Invalid option")


if __name__ == "__main__":
    main()