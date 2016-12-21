#!/usr/bin/env python3

import telebot
import markovify
import os
import logging
import pickle
import re


# Messages
not_enough_text = "Not enough text; keep calm and chat on ;)"
feature_not_enabled = "This feature is not enabled in this chat for now."
no_model_available = "No model available; use /update."
only_group_chat = "This bot only works in a group chat."
model_is_updated = "The model is updated!"
not_enough_arguments = "Not enough arguments."
admin_group_added = "The group has been added to the admin list."
admin_group_removed = "This group has been removed from the admin list."
already_admin_group = "This is already an admin chat."
was_not_enabled = "This group was not enabled."
no_admin_rights = "You have no power here!"


# Config
admin_chat_ids = [
]

admin_user_ids = [
]


with open('store.pckl', 'rb') as read_enabled_chat_save:
    try:
        fully_enabled_chats = pickle.load(read_enabled_chat_save)
    except EOFError as _:
        fully_enabled_chats = []

models = {}

logging.basicConfig(filename='output.log')
logger = logging.getLogger()

with open('token.txt') as token_file:
    token = token_file.read()
bot = telebot.TeleBot(token.strip())


def update_model(message_chat_id):
    if os.path.isfile('text/' + str(message_chat_id) + "-text.txt"):
        with open('text/' + str(message_chat_id) + "-text.txt") as f:
            try:
                models[message_chat_id] = markovify.text.NewlineText(f.read())
            except UnicodeDecodeError:
                pass
    else:
        bot.reply_to(message, not_enough_text)
        logger.info(str(message_chat_id) + ": no text for model")
        return


def has_admin_rights(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    return user_id in admin_user_ids or chat_id in admin_chat_ids


@bot.message_handler(commands=['generate_sentence'])
def next_sentence(message):
    chat_id = message.chat.id

    if chat_id not in fully_enabled_chats:
        bot.reply_to(message, feature_not_enabled)
        return

    if models[chat_id]:
        chat_model = models[chat_id]
        new_msg = chat_model.make_sentence(max_overlap_ratio=0.7, tries=50)
        if new_msg:
            bot.reply_to(message, new_msg)
            return

    bot.reply_to(message, no_model_available)


@bot.message_handler(commands=['update'])
def handle_update(message):

    if not message.chat.type.endswith("group"):
        bot.reply_to(message, only_group_chat)
        return

    update_model(message.chat.id)
    bot.reply_to(message, model_is_updated)


@bot.message_handler(commands=['admin'])
def handle_admin_function(message):
    if has_admin_rights(message):
        args = message.text.split()

        # Action needed as argument
        if len(args) <= 1:
            bot.reply_to(message, not_enough_arguments)
            return

        if args[1] == "add":
            if message.chat.id not in fully_enabled_chats:
                fully_enabled_chats.append(message.chat.id)
                update_model(message.chat.id)
                bot.reply_to(message, admin_group_added)
            else:
                bot.reply_to(message, already_admin_group)

        elif args[1] == "remove":
            if message.chat.id in fully_enabled_chats:
                fully_enabled_chats.remove(message.chat.id)
                bot.reply_to(message, admin_group_removed)
            else:
                bot.reply_to(message, was_not_enabled)
        pickle.dump(fully_enabled_chats, open('store.pckl', 'wb'))
    else:
        log.warn(message.from_user.username + ": no admin rights")
        bot.reply_to(message, no_admin_rights)


@bot.message_handler(func=lambda m: True)
def save_message(message):
    print(message)
    if message.chat.id not in fully_enabled_chats:
        return
    try:
        with open('text/' + str(message.chat.id) + "-text.txt", 'a+') as f:
            f.write(re.sub(r'[^\x00-\x7F]+', '', message.text))
            f.write("\n")
    except UnicodeEncodeError as e:
        pass


for chat in fully_enabled_chats:
    update_model(chat)

while True:
    try:
        bot.polling(none_stop=True)
    except ConnectionError:
        pass
