import telebot
from telebot import types

from settings import config
from db_handler import User, Chat, Category, Transaction
from lexicon import commands, messages, currency, separator


bot = telebot.TeleBot(config.bot.token)


def check_cancel(func):
    def wrapper(message):
        if message.text == commands.cancel:
            return process_cancel(message)
        else:
            return func(message)
    return wrapper


def process_cancel(message):
    Chat.reset(message)
    msg = messages.memory_cleared
    bot.send_message(message.chat.id, msg, reply_markup=get_markup(message))


def base_check(func):
    """Decorator checks if user and chat exists"""
    def wrapper(message):
        if not User.get(message):
            if not User.add(message):
                msg = messages.error_adding_user
                bot.send_message(message.chat.id, msg)

        if not Chat.get(message):
            msg = messages.creating_new_wallet
            next_step = bot.send_message(message.chat.id, msg)
            return bot.register_next_step_handler(next_step, set_balance)

        return func(message)
    return wrapper


def set_balance(message):
    if Chat.add(message):
        msg = messages.new_wallet_created
        markup = get_markup(message)
        bot.send_message(message.chat.id, msg, reply_markup=markup)
    else:
        msg = messages.try_again
        next_step = bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(next_step, set_balance)


def get_markup(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                       resize_keyboard=True)
    memory = Chat.get(message).memory.split(separator)
    if memory[0] == commands.none:
        for command in commands.main_menu.values():
            markup.row(command)
    elif memory[0] == commands.main_menu.report:
        if len(memory) == 1:
            for year in Transaction.get_years(message):
                markup.row(year)
        if len(memory) == 2:
            for month in Transaction.get_months(message):
                markup.row(month)
    elif memory[0] in commands.main_menu.values():
        if memory[0] == commands.main_menu.expense and len(memory) == 2:
            for category in Category.get_subcategories(message):
                markup.row(category)
        elif len(memory) == 1:
            for category in Category.get_all(message):
                markup.row(category)
    if memory[0] != commands.none:
        markup.row(commands.cancel)
    return markup


@check_cancel
def select_category(message):
    Chat.set(message)
    Category.add(message)
    memory = Chat.get(message).memory.split(separator)
    markup = get_markup(message)
    if memory[0] == commands.main_menu.expense and len(memory) == 2:
        msg = messages.select_subcategory
        next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
        bot.register_next_step_handler(next_step, select_category)
    else:
        msg = messages.input_value
        next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
        bot.register_next_step_handler(next_step, input_value)


@check_cancel
def select_year(message):
    Chat.set(message)
    msg = messages.select_month
    markup = get_markup(message)
    next_step = bot.send_message(message.chat.id, msg, reply_markup=markup)
    bot.register_next_step_handler(next_step, select_month)


@check_cancel
def select_month(message):
    Chat.set(message)
    msg = Transaction.get_report(message)
    Chat.reset(message)
    markup = get_markup(message)
    bot.send_message(message.chat.id, msg, reply_markup=markup)


@check_cancel
def input_value(message):
    if not Transaction.add(message):
        msg = messages.try_again
        next_step = bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(next_step, input_value)
    else:
        Chat.reset(message)
        msg = messages.transaction_success
        markup = get_markup(message)
        bot.send_message(message.chat.id, msg, reply_markup=markup)


@bot.message_handler(commands=['start'])
@base_check
def process_start(message):
    process_cancel(message)


@bot.message_handler(content_types=['text'])
@check_cancel
@base_check
def process_message(message):
    if message.text in commands.main_menu.values():
        Chat.set(message)
        if message.text == commands.main_menu.report:
            msg = messages.select_year
            markup = get_markup(message)
            next_step = bot.send_message(message.chat.id, msg,
                                         reply_markup=markup)
            bot.register_next_step_handler(next_step, select_year)
        elif message.text == commands.main_menu.balance:
            Chat.reset(message)
            msg = Chat.get(message).balance + ' ' + currency
            markup = get_markup(message)
            bot.send_message(message.chat.id, msg, reply_markup=markup)
        else:
            msg = messages.select_category
            markup = get_markup(message)
            next_step = bot.send_message(message.chat.id, msg,
                                         reply_markup=markup)
            bot.register_next_step_handler(next_step, select_category)
    else:
        msg = messages.error
        markup = get_markup(message)
        bot.send_message(message.chat.id, msg, reply_markup=markup)


if __name__ == '__main__':
    bot.polling(none_stop=True)
