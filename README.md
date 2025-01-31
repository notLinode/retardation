This is a repository for an **AI Discord bot**.

The bot utilizes LLM's such as Meta's Llama to send messages in Discord channels after every couple of user messages.

The default command prefix is a **semicolon** (`;`). It can only be changed by modifying the source code. A list of most of the bot's commmands can be viewed with `;help`.

The bot has an economy where the money is called **tokens**. Tokens are given to users for texting or they're given hourly when AFK. Tokens can be spent on upgrades, given to other users, or gambled away in blackjack.

The bot also constantly displays a status with its **health**, **hunger**, and **litterbox fullness**. If the bot is allowed to die by starving to death or by intentionally hurting it, it will refuse to do anything until it is revived. Starving can be disabled with the `;do-tamagotchi` command.

# Setting up

First, you'll need to clone the repository with
```
$ git clone https://github.com/notLinode/retardation.git
```
After that, you'll need to `cd` into the cloned repo and create a `tokens.txt` file.
```
$ cd retardation
$ touch tokens.txt
```

The *first line* of `tokens.txt` should be your **Discord bot token** and the *second line* should be your **[Akash Chat API](https://chatapi.akash.network/) token**.

To run the bot, you'll need *Python 3.11* or higher installed along with the *discord.py*, *openai*, and *requests* libraries.
```
$ pip install discord.py, openai, requests
```

After you've installed the neccessary packages and created a `tokens.txt` file, you can launch the bot by running
```
$ python3 src/main.py
```

Each instance of this bot is meant to be used by a __**single Discord server only**__.

# Internal structure

The main entry point of the bot is `main.py`. All of the commands and some other functionality like automessaging is contained in `commands.py`. Talking to Akash Chat API is done in `get_ai_response.py`. Stuff that needs to happen periodically, like updating the bot's status or the shop, is done in `tasks.py`.

All of the values that need to be passed around, (i.e. settings, upgrades, chat history) are defined in `bot_variables.py`. The bot uses a single instance of the `BotVariables` class to pass all of the important values between functions. The variable containing this instance is usually named `bot_vars`.

Now, I say the values are passed around, but in reality functions that use `bot_vars` don't explicitly accept it as a parameter. Instead, if a function uses `bot_vars`, it will access it through a variable defined somewhere at the top of its module.

Most of the values from `bot_vars` are saved on disk (`data/bot_vars.csv`) once every minute by a task. I'm unsure on how healthy this is for SSD's.