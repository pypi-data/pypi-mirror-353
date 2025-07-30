PARSBALE
This library is built by ABAS.
Installation
To install the PARSBALE library, use the following command:
pip install parsbale

Getting the Token
Obtain your bot token from BotFather on the Bale messaging platform.
Example Code



from parsbale import Bot

token = 'token bale bot'  # Replace with your bot token
bot = Bot(token)

@bot.on_message()
async def start_handler(message):
    if message.text == "/start":
        await message.reply("Hello! Welcome to the bot :)")

bot.run()

