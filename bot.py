import discord
from discord.ext import commands
import json
import os
import logging
import re

# Logging setup
logging.basicConfig(level=logging.INFO)

# Bot Setup
TOKEN = "DISCORD_TOKEN"  # Replace with your actual bot token
intents = discord.Intents.default()
bot = commands.Bot(command_prefix=".", intents=intents)

# Constants
FILE_NAME = 'codes.json'
REMOVED_FILE_NAME = 'used.json'

# Helper functions
def load_codes(file_name=FILE_NAME):
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            logging.error("JSON file is corrupted. Resetting to empty data.")
            return {"codes": []}
    return {"codes": []}

def save_codes(data, file_name=FILE_NAME):
    try:
        with open(file_name, 'w') as file:
            json.dump(data, file, indent=4)
    except IOError as e:
        logging.error(f"Error saving file: {e}")

def get_codes(amount, count=1):
    data = load_codes(FILE_NAME)
    group = next((item for item in data['codes'] if item['amount'] == amount), None)

    if not group:
        return None
    
    available_codes = [code for code in group['codes'] if not code['redeemed']]
    
    if len(available_codes) < count:
        return None

    selected_codes = available_codes[:count]
    for code in selected_codes:
        code['redeemed'] = True
    
    # Remove the redeemed codes from the original list
    group['codes'] = [code for code in group['codes'] if not code['redeemed']]
    save_codes(data, FILE_NAME)
    
    return amount, [code['code'] for code in selected_codes]

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
    logging.info(f"Moved {len(used_codes)} used codes to {destination_file}")

# New function to check used codes with pricing in used.json
def check_removed_codes(file_name=REMOVED_FILE_NAME):
    data = load_codes(file_name)
    if not data['codes']:
        return "No Dues available, All clear ✅✅✅."
    
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
    return "\n".join(result)

# New function to check stock with total sum
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
        result.append(f"{amount} 🆄︎🅲︎ ➪ {available_codes} pcs")

    result.append(f"\nWᴏʀᴛʜ Oғ : {total_sum} tk")
    print("\n".join(result))











#creating a total due file 

TOTAL_DUE_FILE = 'total_due.json'

def load_total_due():
    if os.path.exists(TOTAL_DUE_FILE):
        try:
            with open(TOTAL_DUE_FILE, 'r') as file:
                return json.load(file).get('total_due', 0)
        except json.JSONDecodeError:
            logging.error("JSON file is corrupted. Resetting to zero.")
            return 0
    return 0

def save_total_due(amount):
    try:
        with open(TOTAL_DUE_FILE, 'w') as file:
            json.dump({'total_due': amount}, file, indent=4)
    except IOError as e:
        logging.error(f"Error saving total due amount: {e}")

total_due = load_total_due()


# Function to process orders and generate the desired output format
def process_order(amount, count):
    global total_due
    result = get_codes(amount, count)
    if result:
        amount, codes = result
        codes_output = '\n'.join(codes)
        
        data = load_codes(FILE_NAME)
        group = next((item for item in data['codes'] if item['amount'] == amount), None)
        if group:
            price = group.get('price', 0)
            total_due += price * count  # Increment total_due
            save_total_due(total_due)  # Save total_due to file
        
        order_output = f"{codes_output}\n\n✓ {amount} 🆄︎🅲︎  x  {count}  ✓\n"
        order_output += f"Tᴏᴛᴀʟ Dᴜᴇ : {total_due - (price * count)} + ({price}x{count}) = {total_due} tk"
        return order_output
    else:
        logging.warning(f"Not enough available {amount}uc codes.")
        return None


# Bot Commands

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    logging.info("Bot is ready!")

@bot.command()
async def baki(ctx, amount: int, count: int = 1):
    """Retrieve UC codes"""
    result = process_order(amount, count)
    if result:
        await ctx.send(result)
        move_used_codes([{"code": code, "redeemed": True} for code in result.split('\n') if code], amount)
    else:
        await ctx.send(f"❌ Not enough available {amount} UC codes.")

@bot.command()
async def price(ctx, amount: int, price: float):
    """Set the price for a UC package"""
    set_price(amount, price)
    await ctx.send(f"✅ Price for {amount} UC set to {price}.")

@bot.command()
async def clear(ctx):
    """Clear used codes and reset total due"""
    global total_due
    total_due = 0
    save_total_due(total_due)  # Reset total due amount to zero
    save_codes({"codes": []}, REMOVED_FILE_NAME)  # Clear used.json
    await ctx.send("Cleared all dues ✅ ✅.")


@bot.command()
async def rate(ctx):
    """Show UC prices"""
    data = load_codes()
    if not data['codes']:
        await ctx.send("No UC codes available.")
        return
    
    result = []
    for group in data['codes']:
        amount = group['amount']
        price = group.get('price', None)
        if price is not None and price > 0:
            result.append(f"☞ {amount} 🆄︎🅲︎ ➪ {price} BDT")
    
    if not result:
        await ctx.send("No prices set for UC codes.")
    else:
        await ctx.send("\n".join(result))

@bot.command()
async def stock(ctx):
    """Check stock with total sum"""
    data = load_codes()
    if not data['codes']:
        await ctx.send("No codes available.")
        return
    
    total_sum = 0
    result = []
    for group in data['codes']:
        amount = group['amount']
        available_codes = len([code for code in group['codes'] if not code['redeemed']])
        price = group.get('price', 0)
        total_value = price * available_codes
        total_sum += total_value
        result.append(f"{amount} 🆄︎🅲︎ ➪ {available_codes} pcs")

    result.append(f"\nWᴏʀᴛʜ Oғ : {total_sum} tk")
    await ctx.send("\n".join(result))

@bot.command()
async def check(ctx):
    """Check removed codes with total sum"""
    result = check_removed_codes()
    await ctx.send(result)

# Run the bot
bot.run(TOKEN)
