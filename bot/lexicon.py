from dotmap import DotMap

COMMANDS = {
    'cancel': 'Отмена',
    'none': 'None',
    'main_menu': {
        'income': 'Доход',
        'expense': 'Расход',
        'balance': 'Баланс',
        'report': 'Отчет',
    }
}

MESSAGES = {
    'new_user_added': 'Новый пользователь добавлен.',
    'error_adding_user': 'Ошибка добавления пользователя.',
    'creating_new_wallet': 'Похоже, это новый кошелек.\n\
Давай установим текущий баланс.',
    'new_wallet_created': 'Кошелек успешно добавлен.',
    'try_again': 'Попробуй еще разок.',
    'memory_cleared': 'Память почистили.',
    'select_category': 'Выбери категорию:',
    'select_subcategory': 'Выбери подкатегорию:',
    'select_year': 'Выбери год:',
    'select_month': 'Выбери месяц:',
    'error': 'Ошибочка вышла',
    'input_value': 'Введи сумму:',
    'transaction_success': 'Есть!',
    'report': 'Отчет',
}

currency = 'byn'
separator = ' > '

commands = DotMap(COMMANDS)
messages = DotMap(MESSAGES)
