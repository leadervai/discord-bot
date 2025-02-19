Discord UC Code Management Bot

This is a Discord bot that helps manage UC codes by providing functionalities to check prices, stock, and removed codes.

Features

Rate Command (!rate): Displays the UC prices.

Stock Command (!stock): Checks available UC codes and their total worth.

Check Command (!check): Shows removed UC codes with a total sum.


Installation & Setup

Prerequisites

Python 3.8+

discord.py library (Install using pip install discord.py)


Installation

1. Clone this repository:

git clone https://github.com/your-repo/discord-bot.git
cd discord-bot


2. Install required dependencies:

pip install -r requirements.txt


3. Set up your bot token securely:

Create a .env file and add your bot token:

TOKEN=your_discord_bot_token

Alternatively, set the token as an environment variable.




Usage

Run the bot using:

python bot.py

Commands

Error Handling & Logging

If load_codes() or check_removed_codes() fails, the bot will notify the user.

All errors are handled gracefully to prevent crashes.


Contributing

Feel free to submit pull requests or report issues.

