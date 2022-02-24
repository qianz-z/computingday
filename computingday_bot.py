from asyncio.windows_events import NULL
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ParseMode,
)

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler,
    InlineQueryHandler
)

from keys import API_KEY

#757010830
ADMIN_LIST = [
    
]

# To assign each status to a number


_STATES = [
    'MAIN_MENU',
    'USE_ITEMS',
    'USE_ITEMS2',
    'REGISTER',
    'REGISTER_NAME',
    'REGISTER_NAME_CONFIRM',
    'BASE_DECLARE2',
    'BASE_DECLARE3',
    'ADMIN_MENU',
    'ADMIN_GIVE_ITEM_NEXT',
    'ADMIN_ITEM_CONFIRMATION',
]

ITEMS_OFFENSIVE = ['hammer', 'chainsaw', 'pistol', 'axe', 'barrett']

ITEMS_DEFENSIVE = ['potion', 'base_mover']
 

# Set some state variables
# MAIN_MENU, USE_ITEMS, USE_ITEMS2, REGISTER, REGISTER_NAME, REGISTER_NAME_CONFIRM, ADMIN_MENU = range(7)
for i, state in enumerate(_STATES):
    globals()[state] = i
 


def start(update, context):
    chat_id = update.effective_chat.id
    if "registered" in context.user_data and context.user_data['registered']:
        return main_menu(update, context)

    if chat_id in ADMIN_LIST:
        text = "Welcome to the exclusive ADMINS ONLY page!!!!"
        update.message.reply_text(text)
        context.user_data['admin_giveitem_group'] = None
        return admin_main_menu(update, context)

    # What users will receive    
    text = "Welcome to Computing Day Mass Game! "
    update.message.reply_text(text)
    context.user_data["registered"] = False
    context.user_data["group_name"] = None
    print("Someone started the bot!")
    return main_menu(update, context)

# ====================  USER FUNCTIONS ====================
def main_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("Arena status", callback_data='arena_status'), ],
        [InlineKeyboardButton("Rules", callback_data='rules'), ],
        [InlineKeyboardButton("Use items", callback_data='use_items'), ],
        [InlineKeyboardButton("Base Declaration", callback_data='base_declare'), ],
    ]
    if not context.user_data['registered']:
        keyboard.append(
            [InlineKeyboardButton("Register", callback_data='register'), ],
        )

    text = "Pick an option!"
    update.message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard))
    return MAIN_MENU

def base_declare(update, context):
    text = "Where is your base located at?"
    update.callback_query.message.chat.send_message(text)
    return BASE_DECLARE2

def base_declare2(update, context):
    userinput = update.message.text
    group_name = context.user_data['group_name']
    group = context.bot_data['groups'][group_name]
    group['base'] = userinput

    text = "Please send us a picture of the location of your base."
    update.message.reply_text(text)
    return BASE_DECLARE3

def base_declare3(update, context):
    group_name = context.user_data['group_name']
    text = "Thanks! An admin will be verifying ,.."
    update.message.reply_text(
        text
    )
    
    print(update.message.photo)
    group_name = context.user_data['group_name']
    group = context.bot_data['groups'][group_name]
    base = group['base']
    for admin in ADMIN_LIST:
        context.bot.send_photo(
                admin,
                photo=update.message.photo[-1].file_id,
                caption=f"Received from group: {group_name}\n"
                    f"Base located at: {base}"
        )
    
    
    
    
    
    
    
    return MAIN_MENU


def arena_status(update, context):
    text = "Here are the healths of the current groups.\n"
    for group_name in context.bot_data["groups"]:
        # group will store all the key-value pairs in the dictionary
        group = context.bot_data["groups"][group_name]
        group_name = group["group_name"]
        group_health = group["health"]
        text += f"{group_name}: {group_health}\n"
        
    update.callback_query.message.chat.send_message(text)


def rules(update, context):
    text = "Below are the rules of the game"
    update.callback_query.message.chat.send_message(text)


def register(update, context):
    text = 'Please enter your group name below.'
    # Reply to the query that the user sent
    update.callback_query.message.chat.send_message(text)
    return REGISTER_NAME


def confirm_register(update, context):
    group_name = update.message.text
    context.user_data['group_name'] = group_name

    if group_name not in context.bot_data['groups']:
        text = f"{group_name} will be the your group name. Confirm?"
        # Reply to the message that the user sent
        update.message.reply_text(
            text, reply_markup=ReplyKeyboardMarkup([['Yes', 'No']]))
        return REGISTER_NAME_CONFIRM
    else:
        text = f"{group_name} is taken. Please choose a different group name"
        update.message.reply_text(text)
        return REGISTER_NAME

def register_change(update, context):
    text = 'Please enter your group name below.'
    # Reply to the query that the user sent
    update.message.reply_text(text)
    return REGISTER_NAME


def register_done(update, context):
    text = "Yay! Congratz."
    update.message.reply_text(text) #NEED TO REMOVE KEYBOARD
    group_name = context.user_data['group_name']

    context.bot_data['groups'][group_name] = {
        'group_name': group_name,
        'health': 200,
        'items': [],
        'base': None
    }
    
    return MAIN_MENU


def use_item(update, context):
    group_name = context.user_data["group_name"]
    items = context.bot_data['groups'][group_name]['items']
    keyboard = []
    for item in items:
        keyboard.append([InlineKeyboardButton(item, callback_data=item)])
    

    text = "Which item would you like to use?"
    update.message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return USE_ITEMS

def use_item2(update, context):
    item = update.callback_query.data
    
    if item in ITEMS_DEFENSIVE:
        return

    
    text = ""
    update.message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return USE_ITEMS
    


# ==================== ADMIN FUNCTIONS ====================
def admin_main_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("Arena status", callback_data='arena_status'), ],
        [InlineKeyboardButton("Give items", callback_data='admin_give_items'), ],
    ]

    text = "ADMIN MENU"
    update.message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard))
    return ADMIN_MENU

def admin_arena_status(update, context):
    text = "ADMIN ARENA STATUS\n"
    for group_name in context.bot_data["groups"]:
        # group will store all the key-value pairs in the dictionary
        group = context.bot_data["groups"][group_name]
        group_name = group["group_name"]
        group_health = group["health"]
        text += f"{group_name}: {group_health}\n"
        
    update.callback_query.message.chat.send_message(text)

# Choose which group to give
def admin_give_items(update, context):
    text = "Pick a group to give the item to!"
    keyboard = []
    for group_name in context.bot_data["groups"]:
        keyboard.append([InlineKeyboardButton(group_name, callback_data=group_name)])

    update.callback_query.message.chat.send_message(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )
    # Reply to the query that the user sent
    return ADMIN_GIVE_ITEM_NEXT

# Choose which item to give to the group
def admin_give_items2(update, context):
    
    group_name = update.callback_query.data
    context.user_data['admin_giveitem_group'] = group_name
    
    text = f"Pick an item to give {group_name}!"
    keyboard = [
        [InlineKeyboardButton("Hammer", callback_data='hammer'), ],
        [InlineKeyboardButton("Sword", callback_data='sword'), ],
    ]
    update.callback_query.message.chat.send_message(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ADMIN_ITEM_CONFIRMATION

def admin_give_items3(update, context):
    # Getting the answer from callback_data in the prev function
    item = update.callback_query.data
    group_name = context.user_data['admin_giveitem_group']

    text = f"You've given {group_name} the item: {item}"
    
    context.bot_data['groups'][group_name]['items'].append(item)

    update.callback_query.message.chat.send_message(text)
    
    print(context.bot_data)
    
    return ADMIN_MENU




if __name__ == '__main__':
    top_conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            # current status: whatisreceivedfromuser(function to be called, pattern  = 'callback_data')
            MAIN_MENU: [
                CallbackQueryHandler(arena_status, pattern='arena_status'),
                CallbackQueryHandler(register, pattern='register'),
                CallbackQueryHandler(rules, pattern='rules'),
                CallbackQueryHandler(base_declare, pattern='base_declare'),
            ],
            REGISTER_NAME: [
                MessageHandler(Filters.text, callback=confirm_register),
            ],
            REGISTER_NAME_CONFIRM: [
                MessageHandler(Filters.regex("Yes"), callback=register_done),
                MessageHandler(Filters.regex("No"), callback=register_change),
            ],
            USE_ITEMS:[
                CallbackQueryHandler(use_item2),
            ],
            BASE_DECLARE2:[
                MessageHandler(Filters.text, callback=base_declare2)
            ],
            BASE_DECLARE3:[
                MessageHandler(Filters.all, callback=base_declare3)
            ],
            ADMIN_MENU: [
                CallbackQueryHandler(arena_status, pattern='arena_status'),
                CallbackQueryHandler(admin_give_items, pattern='admin_give_items'),
            ],
            ADMIN_GIVE_ITEM_NEXT:[
                # Will go to this function no matter which group is pressed
                CallbackQueryHandler(admin_give_items2),
            ],
            ADMIN_ITEM_CONFIRMATION:[
                CallbackQueryHandler(admin_give_items3),
            ]
        },
        # if it is not in entry point or in state
        fallbacks=[
            CommandHandler('menu', callback=main_menu)
        ]
    )

    updater = Updater(API_KEY)
    dispatcher = Updater(API_KEY)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(top_conv)

    group1 = {
        'group_name': "Group1",
        'health': 200,
        'items': []

    }
    group2 = {
        'group_name': "Group2",
        'health': -999999999999999990,
        'items': []
    }
    dispatcher.bot_data['groups'] = {e['group_name']: e for e in [group1, group2]}
    
    # temp_dict = {}
    # for group in [group1, group2]:
    #     temp_dict[group['group_name']] = group
    #     print(temp_dict)
    # dispatcher.bot_data['groups'] = temp_dict

    
    # dispatcher.bot_data['groups'] = {}
    # print(dispatcher.bot_data['groups'])

    updater.start_polling()
    updater.idle()
