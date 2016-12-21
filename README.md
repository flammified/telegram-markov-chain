# Markov telegram bot

Markovbot is a telegram bot which utilises markov chains to generate new text based on chat messages in group chats.

# Usage

First, install all dependencies in requirements.txt. Then add your token to token.txt, add your chat id or user id into the config in markov.py and run ``` python markov.py```.
When this is done, add the bot to a group chat and enable it for that chat using /admin add. When you think you have enough text, use /update and then /generate_sentence.
