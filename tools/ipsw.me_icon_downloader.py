# by broken_cursor
# 2021

import requests as r
import re
import os

main_page_url = 'https://ipsw.me'

# Get page, find all products
main_page = r.get(main_page_url).text
products = re.findall(
    r"<a class=\"product\" href=\"/product/(.*)\">", main_page)
print('Products:', *products, sep='\n')

for prod in products:
    # Create directory for product
    print('Dowloading icons for', prod)
    prod_dir_path = './icons/' + prod
    os.makedirs(prod_dir_path)

    # Get info about every device on product page:
    # Path to icon file, icon file name, model name
    product_page = r.get(main_page_url + '/product/' + prod).text
    devices = re.findall(
        r"<img src=\"(/assets/devices/(.*))\" alt=\"(.*)\">", product_page)
    for file_path, file_name, model in devices:
        icon_url = main_page_url + file_path
        print('Downloading icon for', model, 'from', icon_url) # For looks
        icon = r.get(icon_url).content # Download icon
        
        # Save icon
        with open(prod_dir_path + '/' + file_name, 'wb') as f:
            f.write(icon)
        f.close()
print('Done!')
