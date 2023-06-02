# Happy Birthday chat bot
An interactive chat bot that can store and send memes, tik-toks and greeting, which was written as a birthday gift.

## Status: In progress

## Features

- **Diversity**: the bot is able to store memes, tik-toks and greetings
- **Convenience**: memes, greetings and tik-toks are uploaded using simple commands in the chat bot.
- **Simple operation**: the ability to easily control the bot from the chat (block and unblock users and other commands)
- **Error Handling**: Correctly detect errors and handle them by providing informative messages and troubleshooting options.

## Installation
To install and run the Report automation application, follow these steps:

1. **Clone repository**: git clone https://github.com/emphat1cBaby/hb-vk-chat-bot.git
2. **Go to the project directory**: cd hb-vk-chat-bot
3. **Install dependencies**: pip install -r requirement.txt
4. **Create a VK community, enable the ability to connect a bot and generate a key**
5. **Create your own config.py file from config.py.default**
6. **Migrate models**
7. **Deploy bot on server**


## Usage
In order to start using the bot, just send him a message with the command.

**List of commands**:

- **Get commands** 
  - *mem* - the command to get a meme.
  - *tt* - the command to get a tik-tok.
  - *greeting* - the command to get a greeting.
- **Load commands**
  - *loadmem* - the command to get a meme to bot db.
  - *loadtt* - the command to get a tik-tok to bot db.
  - *loadgreeting* - the command to get a greeting to bot db.
- **Admin commands**
  - *ban_chat* - the command to ban a chat.
  - *unban_chat* - the command to unban a chat.
- **Other commands**
  - *help* - command to receive a message with instructions to the bot.


## Authors
Dmitriy Smirnov - https://t.me/emphaticBaby

## Stack
1. *Library vkwave* - for working with the VKontakte API in Python. It provides convenient and easy-to-use tools for interacting with the VK API, allowing developers to create applications, bots and scripts to automate tasks on the VKontakte social network.
2. *Library pony orm* - simple, fast and intuitive object-relational system for working with databases in Python.
