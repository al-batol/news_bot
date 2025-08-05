#!/usr/bin/env python3
import re
import requests

# Test manual description extraction
url = 'https://www.coindesk.com/arc/outboundfeeds/rss/'
response = requests.get(url)
rss_content = response.text

# Extract descriptions manually
descriptions_map = {}
items = re.findall(r'<item>(.*?)</item>', rss_content, re.DOTALL)

for i, item in enumerate(items[:3]):  # Test first 3 items
    # Extract link
    link_match = re.search(r'<link>(.*?)</link>', item)
    if not link_match:
        continue
    link = link_match.group(1).strip()
    
    # Extract description from CDATA
    desc_match = re.search(r'<description>\s*<!\[CDATA\[(.*?)\]\]>\s*</description>', item, re.DOTALL)
    if desc_match:
        description = desc_match.group(1).strip()
        descriptions_map[link] = description
        print(f'Item {i+1}:')
        print(f'Link: {link}')
        print(f'Description: {description[:150]}...')
        print('---')

print(f'Total descriptions extracted: {len(descriptions_map)}')