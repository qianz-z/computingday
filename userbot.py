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
    REG_TYPING_NAME,
    REG_CONFIRMING_NAME,
    REG_TYPING_BASE,
    REG_SENDING_BASE_PHOTO,
    REG_CHOOSING_HERO,
)
from hero import HEROS
from keys import CHAT_PARTICIPANTS, CHAT_ADMINS
from helpers import get_group


def main_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("Arena status", callback_data='arena_status')],
        [InlineKeyboardButton("Rules", callback_data='rules')],
    ]
    if not context.user_data['group_name']:
        keyboard.append([InlineKeyboardButton("Register", callback_data='register')])
    else:
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
    update.callback_query.message.reply_text(text)
    return REG_TYPING_NAME


def register_confirm(update, context):
    group_name = update.message.text
    context.user_data['group_name'] = group_name

    if group_name in context.bot_data['groups']:
        text = f"{group_name} is taken. Please choose a different group name."
        update.message.reply_text(text)
        return REG_TYPING_NAME

    text = f"{group_name} will be the your group name. Confirm?"
    # Reply to the message that the user sent
    update.message.reply_text(
        text, reply_markup=ReplyKeyboardMarkup([['Yes', 'No']]))
    return REG_CONFIRMING_NAME


def register_change(update, context):
    text = 'Please enter your group name below.'
    # Reply to the query that the user sent
    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    return REG_TYPING_NAME


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
    return REG_CHOOSING_HERO

def register_trap(update, context):
    msg = update.message or update.callback_query.message
    msg.reply_text("You must complete the register procedure first!")


def choose_hero_confirm(update, context):
    group_name = context.user_data['group_name']
    hero = update.callback_query.data
    class_constructor = HEROS[hero]
    group = class_constructor(group_name, update.effective_user.id)
    context.user_data['group_name'] = group_name
    context.bot_data['groups'][group_name] = group
    
    group.hero = hero

    text = f"Your hero is {hero}.\n"

    
    update.callback_query.message.reply_text(text)
    text = "Now choose your base location."
    update.callback_query.message.reply_text(text)
    return REG_TYPING_BASE


def base_declare2(update, context):
    userinput = update.message.text
    group = get_group(context)
    group.base = userinput

    text = "Please send us a picture of the location of your base."
    update.message.reply_text(text)
    return REG_SENDING_BASE_PHOTO


def base_declare3(update, context):
    text = "Thanks! An admin will be verifying ... \n Use /menu to find out what you can do with this bot"
    update.message.reply_text(text)
    group = get_group(context)
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

    return ConversationHandler.END

register_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(register, pattern='register')],
    states={
        REG_TYPING_NAME: [
            MessageHandler(Filters.text & ~Filters.command, callback=register_confirm),
        ],
        REG_CONFIRMING_NAME: [
            MessageHandler(Filters.regex("Yes"), callback=register_done),
            MessageHandler(Filters.regex("No"), callback=register_change),
        ],
        REG_CHOOSING_HERO: [
            CallbackQueryHandler(choose_hero_confirm),
        ],
        REG_TYPING_BASE: [
            MessageHandler(Filters.text & ~Filters.command, callback=base_declare2)
        ],
        REG_SENDING_BASE_PHOTO: [
            MessageHandler(Filters.all, callback=base_declare3)
        ],
    },
    fallbacks=[
        MessageHandler(Filters.command, callback=register_trap),
        CallbackQueryHandler(callback=register_trap),
    ],
    name='register_conv',
    persistent=True
)


def use_item(update, context):
    group = get_group(context)
    items = group.items
        
    print("group with obj id ", id(group))
    if len(items) == 0:
        update.callback_query.message.reply_text(
            "You have no items with you currently!")
        return

    keyboard = []
    for item in items:
        keyboard.append([InlineKeyboardButton(item, callback_data=item)])

    text = "Which item would you like to use?"
    update.callback_query.message.reply_text(
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
    update.callback_query.message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard))

    return USE_ITEMS2


def use_item_done(update, context):
    other_group_name = update.callback_query.data
    other_group = context.bot_data['groups'][other_group_name]
    group = get_group(context)
    item = context.user_data['using_item']

    # Send what happened in participants group
    if item in ITEMS_OFFENSIVE:
        damage = ITEMS_OFFENSIVE[item] * group.strength_multiplier
        other_group.health -= damage
        text = (
            f"Someone has attacked {other_group.group_name}'s base using {item}!\n"
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
            text = (
                f"{other_group.group_name}'s base has just used {item}!"
                f"\n{other_group.group_name}'s base is now {other_group.health}"
            )
        
    group.items.remove(item)
    context.bot.send_message(CHAT_PARTICIPANTS, text)
    context.bot.send_message(CHAT_ADMINS, text)
    
    return ConversationHandler.END

def temp(update, context):
    update.message.reply_text("Hi!")


use_item_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(use_item, pattern='use_items')],
    states={
        USE_ITEMS: [
            CallbackQueryHandler(use_item2),
        ],
        USE_ITEMS2: [
            CallbackQueryHandler(use_item_done),
        ],
        MENU_USER: [MessageHandler(Filters.all, temp)]
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

    update.callback_query.message.reply_text(text)

def status(update, context):
    update.callback_query.delete_message()

    group = get_group(context)
    text = ""
    for key, value in group.__dict__.items():
        text += f"{key}: {value}\n"
    update.callback_query.message.reply_text(text)


def rules(update, context):
    update.callback_query.delete_message()
    text = "Below are the rules of the game"
    update.callback_query.message.reply_text(text)
    update.callback_query.message.reply_text(RULES_TEXT)
    
    
arena_status_cbh = CallbackQueryHandler(arena_status, pattern='arena_status')
group_status_cbh = CallbackQueryHandler(status, pattern='status')
rules_cbh = CallbackQueryHandler(rules, pattern='rules')
