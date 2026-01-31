#!/usr/bin/env python3
# Replace rupee symbol with RS.

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace rupee symbol with RS.
content = content.replace('₹', 'RS.')

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Successfully replaced all ₹ with RS.')
