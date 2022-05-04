from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
)

from const import (
    ITEMS_OFFENSIVE,
    ITEMS_DEFENSIVE,
    RULES_TEXT,
)
from const import (
    MENU_USER,
    USE_ITEMS,
    USE_ITEMS2,
    REGISTER_NAME,
    REGISTER_NAME_CONFIRM,
    BASE_DECLARE2,
    BASE_DECLARE3,
    CHOOSE_HERO,
)
from hero import HEROS
from keys import CHAT_PARTICIPANTS, CHAT_ADMINS


def main_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("Arena status", callback_data='arena_status')],
        [InlineKeyboardButton("Rules", callback_data='rules')],
    ]
    if not context.user_data['group']:
        keyboard.append([InlineKeyboardButton(
            "Register", callback_data='register'), ])

    if context.user_data['group']:
        keyboard.append([InlineKeyboardButton("Use items", callback_data='use_items')])
        keyboard.append([InlineKeyboardButton("Group's Status", callback_data='status')],)

    text = "Pick an option!"
    update.message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard))
    return MENU_USER




def register(update, context):
    update.callback_query.delete_message()

    text = 'Please enter your group name below.'
    # Reply to the query that the user sent
    update.callback_query.message.chat.send_message(text)
    return REGISTER_NAME


def confirm_register(update, context):
    group_name = update.message.text
    context.user_data['group_name'] = group_name

    if group_name in context.bot_data['groups']:
        text = f"{group_name} is taken. Please choose a different group name."
        update.message.reply_text(text)
        return REGISTER_NAME

    text = f"{group_name} will be the your group name. Confirm?"
    # Reply to the message that the user sent
    update.message.reply_text(
        text, reply_markup=ReplyKeyboardMarkup([['Yes', 'No']]))
    return REGISTER_NAME_CONFIRM


def register_change(update, context):
    text = 'Please enter your group name below.'
    # Reply to the query that the user sent
    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    return REGISTER_NAME


def register_done(update, context):
    group_name = context.user_data['group_name']
    text = f"Successfully registered {group_name}."
    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    context.user_data['registered'] = True

    text = "Choose your favourite food"
    keyboard = [
        [InlineKeyboardButton("Fried Chicken", callback_data='bat_girl')],
        [InlineKeyboardButton("Cheese Burger", callback_data='captain_america')],
        [InlineKeyboardButton("Sprite", callback_data='jesse_quick')],
        [InlineKeyboardButton("Iron Supplements", callback_data='iron_man')],
        [InlineKeyboardButton("Fertiliser", callback_data='groot')],
        [InlineKeyboardButton("Icecream", callback_data='six_sense')],
        [InlineKeyboardButton("Vegetable", callback_data='hulk')],
    ]
    update.message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSE_HERO


def choose_hero_confirm(update, context):
    group_name = context.user_data['group_name']
    hero = update.callback_query.data
    class_constructor = HEROS[hero]
    group = class_constructor(group_name, update.effective_user.id)
    context.user_data['group'] = group
    context.bot_data['groups'][group_name] = group
    
    group.hero = hero

    text = f"Your hero is {hero}.\n"

    
    update.callback_query.message.chat.send_message(text)
    text = "Now choose your base location."
    update.callback_query.message.chat.send_message(text)
    return BASE_DECLARE2


def base_declare2(update, context):
    userinput = update.message.text
    group_name = context.user_data['group_name']
    group = context.bot_data['groups'][group_name]
    group.base = userinput

    text = "Please send us a picture of the location of your base."
    update.message.reply_text(text)
    return BASE_DECLARE3


def base_declare3(update, context):
    text = "Thanks! An admin will be verifying ... \n Use /menu to find out what you can do with this bot"
    update.message.reply_text(text)

    group = context.user_data['group']

    keyboard = [[InlineKeyboardButton("Verified", callback_data=group.group_name)]]

    try:
        context.bot.send_photo(
            CHAT_ADMINS,
            photo=update.message.photo[-1].file_id,
            caption=(
                f"Received from group: {group.group_name}\n"
                f"Base located at: {group.base}"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except IndexError:
        print("ErroR!!!")
        print(dir(update.message))

    return MENU_USER

register_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(register, pattern='register')],
    states={
        REGISTER_NAME: [
            MessageHandler(Filters.text & ~Filters.command, callback=confirm_register),
        ],
        REGISTER_NAME_CONFIRM: [
            MessageHandler(Filters.regex("Yes"), callback=register_done),
            MessageHandler(Filters.regex("No"), callback=register_change),
        ],
        CHOOSE_HERO: [
            CallbackQueryHandler(choose_hero_confirm),
        ],
        BASE_DECLARE2: [
            MessageHandler(Filters.text & ~Filters.command, callback=base_declare2)
        ],
        BASE_DECLARE3: [
            MessageHandler(Filters.all, callback=base_declare3)
        ],
    },
    fallbacks=[],
    name='register_conv',
    persistent=True
)


def use_item(update, context):
    group = context.user_data['group']
    items = group.items

    keyboard = []
    for item in items:
        keyboard.append([InlineKeyboardButton(item, callback_data=item)])

    text = "Which item would you like to use?"
    update.callback_query.message.chat.send_message(
        text, reply_markup=InlineKeyboardMarkup(keyboard))
    return USE_ITEMS


def use_item2(update, context):
    item = update.callback_query.data
    context.user_data['using_item'] = item

    keyboard = []
    for group in context.bot_data['groups'].values():
        if group.using_potion:
            continue
        keyboard.append([InlineKeyboardButton(group.group_name, callback_data=group.group_name)])
    
    text = f"Which group to use the {item} on?"
    update.callback_query.message.chat.send_message(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return USE_ITEMS2


def use_item_done(update, context):
    other_group_name = update.callback_query.data
    other_group = context.bot_data['groups'][other_group_name]
    group = context.user_data['group']
    item = context.user_data['using_item']

    # Send what happened in participants group
    if item in ITEMS_OFFENSIVE:
        damage = ITEMS_OFFENSIVE[item] * group.strength_multiplier
        other_group.health -= damage
        text = (f"Someone has attacked {other_group.group_name}'s base using {item}!\n"
               f"{other_group.group_name}'s base is now {other_group.health}"
        )
        
    elif item in ITEMS_DEFENSIVE:
        text = f"{other_group.group_name}'s base has just used {item}!\n"
        if item == 'potion':
            other_group.using_potion = True
            text += f"{other_group.group_name} is invulnerable for 5 minutes!"
            
            def potion_expired(context):
                other_group.using_potion = False
                
                text = f"Tick tock, 5 minutes is up! {other_group.group_name}'s potion effect has subsided. They are now vulnerable!"
                context.bot.send_message(CHAT_PARTICIPANTS, text)
                context.bot.send_message(CHAT_ADMINS, text)

            context.job_queue.run_once(potion_expired, 15)

        elif item == 'base_mover':
            text += f"{other_group.group_name} has just shifted their base to an unknown location. Good luck finding!"
            
        elif item == 'defence_mechanism':
            other_group.health += 100
            text = (f"{other_group.group_name}'s base has just used {item}!\n"
               f"{other_group.group_name}'s base is now {other_group.health}"
            )
        
    group.items.remove(item)
    context.bot.send_message(CHAT_PARTICIPANTS, text)
    context.bot.send_message(CHAT_ADMINS, text)
    
    return MENU_USER


use_item_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(use_item, pattern='use_items')],
    states={
        USE_ITEMS: [
            CallbackQueryHandler(use_item2),
        ],
        USE_ITEMS2: [
            CallbackQueryHandler(use_item_done),
        ],
    },
    fallbacks=[],
    allow_reentry=False,
    name='use_item_conv',
    persistent=True
)


def arena_status(update, context):
    update.callback_query.delete_message()
    text = "Here are the healths of the current groups.\n"
    for group_name in context.bot_data['groups']:
        # group will store all the key-value pairs in the dictionary
        group = context.bot_data['groups'][group_name]
        text += f"{group.group_name}: {group.health}\n"

    update.callback_query.message.chat.send_message(text)

def status(update, context):
    update.callback_query.delete_message()

    group = context.user_data['group']
    text = ""
    for key, value in group.__dict__.items():
        text += f"{key}: {value} \n"
    update.callback_query.message.chat.send_message(text)


def rules(update, context):
    update.callback_query.delete_message()
    text = "Below are the rules of the game"
    update.callback_query.message.chat.send_message(text)
    update.callback_query.message.chat.send_message(RULES_TEXT)
    
    
arena_status_cbh = CallbackQueryHandler(arena_status, pattern='arena_status')
group_status_cbh = CallbackQueryHandler(status, pattern='status')
rules_cbh = CallbackQueryHandler(rules, pattern='rules')
