import discord
from discord.ext import commands
import json
import os
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)

# Retrieve the token from the environment variable
TOKEN = os.getenv('DISCORD_TOKEN')

# Check if the token was retrieved correctly
if TOKEN is None:
    raise ValueError("No Discord token found in environment variables.")

# Bot Setup
intents = discord.Intents.default()
intents.message_content = True  # Enable the Message Content Intent
bot = commands.Bot(command_prefix="!", intents=intents)

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
    
    save_codes(data, FILE_NAME)
    
    return [code['code'] for code in selected_codes]

# Bot Commands

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
async def stock(ctx):
    """Check available UC stock"""
    data = load_codes()
    if not data['codes']:
        await ctx.send("No codes available.")
        return
    
    result = []
    for group in data['codes']:
        amount = group['amount']
        available_codes = len([code for code in group['codes'] if not code['redeemed']])
        result.append(f"✓ {amount} 🆄︎🅲︎ ➪ {available_codes} pcs")

    await ctx.send("\n".join(result))

@bot.command()
async def get(ctx, amount: int, count: int = 1):
    """Retrieve UC codes"""
    codes = get_codes(amount, count)
    if codes:
        codes_output = '\n'.join(codes)
        await ctx.send(f"Here are your {amount} UC codes:\n```\n{codes_output}\n```")
    else:
        await ctx.send(f"❌ Not enough available {amount} UC codes.")

@bot.command()
async def set_price(ctx, amount: int, price: float):
    """Set the price for a UC package"""
    data = load_codes()
    group = next((item for item in data['codes'] if item['amount'] == amount), None)
    
    if not group:
        await ctx.send(f"❌ No UC codes available for {amount}.")
        return
    
    group['price'] = price
    save_codes(data)
    await ctx.send(f"✅ Price for {amount} UC set to {price}.")

@bot.command()
async def remove(ctx):
    """Clear used codes"""
    save_codes({"codes": []}, REMOVED_FILE_NAME)
    await ctx.send("✅ Cleared all used codes.")

@bot.command()
async def rate(ctx):
    """Show UC prices"""
    data = load_codes()
    if not data['codes']:
        await ctx.send("No UC codes available.")
        return
    
    result = []
    seen_amounts = set()
    for group in data['codes']:
        amount = group['amount']
        if amount in seen_amounts:
            continue
        seen_amounts.add(amount)
        price = group.get('price', 0)
        if price > 0:
            result.append(f"☞ {amount} 🆄︎🅲︎ ➪ {price} BDT")

    await ctx.send("\n".join(result))

# Run the bot
bot.run(TOKEN)
