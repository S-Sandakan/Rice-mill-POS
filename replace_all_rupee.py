#!/usr/bin/env python3
# Replace rupee symbol with RS. in all Python files

import os

files_to_update = [
    'main.py',
    'reports.py', 
    'product_manager.py',
    'stock_manager.py',
    'backup.py'
]

for filename in files_to_update:
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace rupee symbol with RS.
        original_content = content
        content = content.replace('₹', 'RS.')
        
        if content != original_content:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'✓ Successfully replaced ₹ with RS. in {filename}')
        else:
            print(f'- No changes needed in {filename}')
    else:
        print(f'✗ File not found: {filename}')

print('\nDone!')
