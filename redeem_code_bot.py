

import json
import os
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO)

# Constants
FILE_NAME = 'codes.json'
REMOVED_FILE_NAME = 'used.json'

# Load codes from JSON file
def load_codes(file_name=FILE_NAME):
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            logging.error("JSON file is corrupted. Resetting to empty data.")
            return {"codes": []}
    return {"codes": []}

# Save codes to JSON file
def save_codes(data, file_name=FILE_NAME):
    try:
        with open(file_name, 'w') as file:
            json.dump(data, file, indent=4)
    except IOError as e:
        logging.error(f"Error saving file: {e}")

# Add codes grouped by amount
def add_codes(amount, codes, file_name=FILE_NAME):
    data = load_codes(file_name)
    group = next((item for item in data['codes'] if item['amount'] == amount), None)
    
    if not group:
        group = {"amount": amount, "codes": [], "price": 0}
        data['codes'].append(group)
    
    existing_codes = {code['code'] for code in group['codes']}
    new_codes = []

    for code in codes:
        if code.strip() not in existing_codes:
            new_codes.append({"code": code.strip(), "redeemed": False})
            existing_codes.add(code.strip())
        else:
            logging.warning(f"Duplicate code detected: {code.strip()}")

    group['codes'].extend(new_codes)
    
    save_codes(data, file_name)
    logging.info(f"Added {len(new_codes)} codes for amount: {amount}")

# Set price for a specific amount in both files
def set_price(amount, price, file_name=FILE_NAME):
    data = load_codes(file_name)
    group = next((item for item in data['codes'] if item['amount'] == amount), None)
    
    if not group:
        logging.warning(f"No codes available for amount: {amount}")
        return
    
    group['price'] = price
    save_codes(data, file_name)
    logging.info(f"Set price for {amount}uc codes to {price}")

    # Also set price in used.json
    if file_name != REMOVED_FILE_NAME:
        data_used = load_codes(REMOVED_FILE_NAME)
        group_used = next((item for item in data_used['codes'] if item['amount'] == amount), None)
        
        if group_used:
            group_used['price'] = price
            save_codes(data_used, REMOVED_FILE_NAME)
            logging.info(f"Set price for {amount}uc codes to {price} in {REMOVED_FILE_NAME}")

# Move used codes to used.json
def move_used_codes(used_codes, amount, destination_file=REMOVED_FILE_NAME):
    destination_data = load_codes(destination_file)

    if 'codes' not in destination_data:
        destination_data['codes'] = []

    destination_group = next((item for item in destination_data['codes'] if item['amount'] == amount), None)
    if not destination_group:
        destination_group = {"amount": amount, "codes": [], "price": 0}  # Include price field
        destination_data['codes'].append(destination_group)
    
    # Include price from codes.json
    source_data = load_codes(FILE_NAME)
    source_group = next((item for item in source_data['codes'] if item['amount'] == amount), None)
    if source_group:
        destination_group['price'] = source_group.get('price', 0)
        
    destination_group['codes'].extend(used_codes)
    save_codes(destination_data, destination_file)
    print(f"Moved {len(used_codes)} used codes to {destination_file}")

# Get and mark codes as redeemed
def get_codes(amount, count=1, source_file=FILE_NAME):
    data = load_codes(source_file)
    group = next((item for item in data['codes'] if item['amount'] == amount), None)
    
    if not group:
        logging.warning(f"No codes available for amount: {amount}")
        return None
    
    available_codes = [code for code in group['codes'] if not code['redeemed']]
    if len(available_codes) < count:
        logging.warning(f"Not enough available {amount}uc codes.")
        return None

    selected_codes = available_codes[:count]
    for code in selected_codes:
        code['redeemed'] = True
    
    used_codes = [code for code in selected_codes if code['redeemed']]
    move_used_codes(used_codes, amount)
    
    group['codes'] = [code for code in group['codes'] if not code['redeemed']]
    save_codes(data, source_file)
    
    return [code['code'] for code in selected_codes]

# Check stock of codes with total sum
def check_stock(file_name=FILE_NAME):
    data = load_codes(file_name)
    if not data['codes']:
        print("No codes available.")
        return
    
    total_sum = 0
    result = []
    for group in data['codes']:
        amount = group['amount']
        available_codes = len([code for code in group['codes'] if not code['redeemed']])
        price = group.get('price', 0)
        total_value = price * available_codes
        total_sum += total_value
        result.append(f"{amount} 🆄︎ 🅲︎ ➪  {available_codes} pcs")

    result.append(f"\nWᴏʀᴛʜ Oғ : {total_sum} tk")
    print("\n".join(result))

# Remove used codes and transfer to used.json
def remove_used_codes(source_file=FILE_NAME, destination_file=REMOVED_FILE_NAME):
    source_data = load_codes(source_file)
    destination_data = load_codes(destination_file)

    if 'codes' not in destination_data:
        destination_data['codes'] = []

    for group in source_data['codes']:
        used_codes = [code for code in group['codes'] if code['redeemed']]
        if used_codes:
            destination_group = next((item for item in destination_data['codes'] if item['amount'] == group['amount']), None)
            if not destination_group:
                destination_group = {"amount": group['amount'], "codes": [], "price": 0}  # Include price field
                destination_data['codes'].append(destination_group)
            
            # Include price from codes.json
            destination_group['price'] = group.get('price', 0)
            
            destination_group['codes'].extend(used_codes)
            group['codes'] = [code for code in group['codes'] if not code['redeemed']]

    save_codes(source_data, source_file)
    save_codes(destination_data, destination_file)
    print("Removed all used codes and saved them to used.json")

# Clear all codes from used.json
def clear_removed_codes(file_name=REMOVED_FILE_NAME):
    empty_data = {"codes": []}
    save_codes(empty_data, file_name)
    print(f"Cleared all codes from {file_name}")

# Check number of codes in used.json grouped by amount with pricing
def check_removed_codes(file_name=REMOVED_FILE_NAME):
    data = load_codes(file_name)
    if not data['codes']:
        print("No codes available in used.json.")
        return

    result = []
    total_sum = 0
    for group in data['codes']:
        amount = group['amount']
        count = len(group['codes'])
        price = group.get('price', 0)  # Get price from the group or default to 0
        total_value = price * count
        total_sum += total_value
        result.append(f"{amount} 🆄︎ 🅲︎ ➪ {count} pcs")
    
    result.append(f"\nTotal due: {total_sum} tk")
    print("\n".join(result))

# Show prices for all existing UC amounts in codes.json
def show_prices():
    data = load_codes(FILE_NAME)
    
    if not data['codes']:
        logging.warning("No UC codes available in the database.")
        return
    
    for group in data['codes']:
        amount = group['amount']
        price = group.get('price', 0)
        
        if price > 0:
            print(f"☞︎︎︎ {amount} 🆄︎ 🅲︎ ➪ {price} Bᴀɴᴋ")
        else:
            logging.warning(f"No price set for {amount}uc")

# Main function to process commands
def process_command(command):
    if command == "rate":
        show_prices()

    elif command.startswith("up"):
        parts = command.split(' ', 2)
        if len(parts) < 3:
            logging.error("Invalid command format. Use: up <amount>uc <codes>")
            return

        amount_code, codes = parts[1], parts[2]
        try:
            amount = int(amount_code[:-2])
        except ValueError:
            logging.error("Invalid amount format. Please provide a valid number before 'uc'.")
            return

        # Extract each code using a flexible pattern
        pattern = r'[a-zA-Z]{4}-[a-zA-Z]-S-\d{8} \d{4}-\d{4}-\d{4}-\d{4}'
        clean_codes = re.findall(pattern, codes)

        if not clean_codes:
            logging.error("No valid codes found.")
            return

        add_codes(amount, clean_codes)

    elif command == "stock":
        check_stock()  # Updated to include total sum

    elif command == "remove codes":
        remove_used_codes()

    elif command == "remove":
        clear_removed_codes()

    elif command == "check":
        check_removed_codes()  # Updated to include pricing info and total sum

    elif command.startswith("set price"):
        parts = command.split()
        if len(parts) != 4:
            logging.error("Invalid command format. Use: set price <amount>uc <price>")
        try:
            amount = int(parts[2][:-2])
            price = float(parts[3])
        except ValueError:
            logging.error("Invalid amount or price format. Please provide valid numbers.")
            return

        set_price(amount, price)

    elif command.endswith("uc"):
        try:
            amount = int(command[:-2])
            count = 1
        except ValueError:
            logging.error("Invalid amount format. Please provide a valid number before 'uc'.")
            return
        
        process_order(amount, count)

    elif "uc" in command:
        parts = command.split()
        try:
            amount = int(parts[0][:-2])
            count = int(parts[1])
        except (ValueError, IndexError):
            logging.error("Invalid command format. Use: <amount>uc <count>")
            return

        process_order(amount, count)
    
    else:
        logging.error("Unknown command. Please try again.")

# Function to process orders and generate the desired output format
def process_order(amount, count):
    codes = get_codes(amount, count)
    if codes:
        codes_output = '\n'.join(codes)
        total_due = 0
        price = None
        
        data = load_codes(FILE_NAME)
        group = next((item for item in data['codes'] if item['amount'] == amount), None)
        if group:
            price = group.get('price', 0)
            total_due = price * count
        
        print(f"{codes_output}\n\n✓ {amount} 🆄︎🅲︎  x  {count}  ✓")
        print(f"Tᴏᴛᴀʟ Dᴜᴇ : {price} + ({price}x{count}) = {total_due} tk")
    else:
        logging.warning(f"Not enough available {amount}uc codes.")

# Main command system for the bot
def main():
    print("Welcome to the Redeem Code Management System!")
    while True:
        command = input("Enter command (or type 'exit' to quit): ").strip()
        if command == "exit":
            print("Exiting the system. Goodbye!")
            break
        process_command(command)

if __name__ == "__main__":
    main()
