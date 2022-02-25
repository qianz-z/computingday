from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
)

from keys import API_KEY, USER_ADMINS, CHAT_PARTICIPANTS, CHAT_ADMINS

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
    'CHOOSE_HERO',
    'CHOOSE_HERO_CONFIRM',
    'ADMIN_MANUAL_UPDATE',
    'ADMIN_MANUAL_UPDATE2',
    'ADMIN_MANUAL_UPDATE3',
    'ADMIN_MANUAL_UPDATE4',
]

ITEMS_OFFENSIVE = {
    'hammer': 150,
    'chainsaw': 50,
    'pistol': 20,
    'axe': 30,
    'barrett': 80
}

ITEMS_DEFENSIVE = ['potion', 'base_mover']


# Set some state variables
# MAIN_MENU, USE_ITEMS, USE_ITEMS2, REGISTER, REGISTER_NAME, REGISTER_NAME_CONFIRM, ADMIN_MENU = range(7)
for i, state in enumerate(_STATES):
    globals()[state] = i



class Group:
    def __init__(self, group_name, transporter):
        self.group_name = group_name
        self.transporter = transporter
        self.health = 200
        self.items = []
        self.base = 1
        self.hero = None
        self.hero_level = 1  # Should be None
        


def start(update, context):
    chat_id = update.effective_chat.id
    if "registered" in context.user_data and context.user_data['registered']:
        return main_menu(update, context)

    if chat_id in USER_ADMINS:
        text = "Welcome to the exclusive ADMINS ONLY page!!!!"
        update.message.reply_text(text)
        context.user_data['admin_giveitem_group'] = None
        context.user_data['admin_manual_group'] = None
        context.user_data['admin_delta_health'] = 0
        return admin_main_menu(update, context)

    # What users will receive
    text = "Welcome to Computing Day Mass Game! "
    update.message.reply_text(text)
    context.user_data["group"] = None
    print("Someone started the bot!")
    return main_menu(update, context)

# ====================  USER FUNCTIONS ====================


def main_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("Arena status", callback_data='arena_status')],
        [InlineKeyboardButton("Rules", callback_data='rules')],
        [InlineKeyboardButton("Use items", callback_data='use_items')],
        [InlineKeyboardButton("Base Declaration", callback_data='base_declare')]
    ]
    if not context.user_data['group']:
        keyboard.append(
            [InlineKeyboardButton("Register", callback_data='register'), ],
        )

    text = "Pick an option!"
    update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    return MAIN_MENU


def base_declare(update, context):
    text = "Where is your base located at?"
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
    text = "Thanks! An admin will be verifying ,.."
    update.message.reply_text(text)

    group = context.user_data['group']
    context.bot.send_photo(
        CHAT_ADMINS,
        photo=update.message.photo[-1].file_id,
        caption=(
            f"Received from group: {group.group_name}\n"
            f"Base located at: {group.base}"
        )
    )

    return MAIN_MENU


def arena_status(update, context):
    text = "Here are the healths of the current groups.\n"
    for group_name in context.bot_data["groups"]:
        # group will store all the key-value pairs in the dictionary
        group = context.bot_data["groups"][group_name]
        text += f"{group.group_name}: {group.health}\n"

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

    if group_name in context.bot_data['groups']:
        text = f"{group_name} is taken. Please choose a different group name."
        update.message.reply_text(text)
        return REGISTER_NAME

    text = f"{group_name} will be the your group name. Confirm?"
    # Reply to the message that the user sent
    update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup([['Yes', 'No']]))
    return REGISTER_NAME_CONFIRM


def register_change(update, context):
    text = 'Please enter your group name below.'
    # Reply to the query that the user sent
    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    return REGISTER_NAME


def register_done(update, context):
    group_name = context.user_data['group_name']
    group = Group(group_name, update.effective_user.id)
    context.bot_data['groups'][group_name] = group
    context.user_data['group'] = group

    text = "Sweet! Send /menu to see what you can do now."
    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    return CHOOSE_HERO


def choose_hero(update, context):
    text = "Choose your favourite food"
    keyboard = [
        [InlineKeyboardButton("Fried Chicken", callback_data='bat_girl')],
        [InlineKeyboardButton("Cheese Burger", callback_data='captain_america')],
        [InlineKeyboardButton("Sprite", callback_data='jesse_quick')],
        [InlineKeyboardButton("Iron Supplements", callback_data='iron_man')],
        [InlineKeyboardButton("Fertiliser", callback_data='groot')],
        [InlineKeyboardButton("Icecream", callback_data='six_sense')],
    ]
    update.callback_query.message.chat.send_message(
        text, reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSE_HERO_CONFIRM
    
def choose_hero_confirm(update, context):
    hero = update.callback_query.data
    group = context.user_data['group']
    group.hero = hero
    return MAIN_MENU


def use_item(update, context):
    group = context.user_data['group']
    items = group.items
    
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


def use_item_done(update, context):
    group_name = context.user_data['group'].group_name
    
    # Send what happened in participants group
    text = f"Someone has attacked {group_name}'s base!"
    context.bot.send_message(CHAT_PARTICIPANTS, text)
    


# ==================== ADMIN FUNCTIONS ====================
def admin_main_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("Arena status", callback_data='arena_status'), ],
        [InlineKeyboardButton("Give items", callback_data='admin_give_items'), ],
        [InlineKeyboardButton("Manual Updates", callback_data='admin_manual_update'), ],
    ]
    text = "Welcome to the admin menu! Choose an action!"
    update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    return ADMIN_MENU

def admin_manual_update1(update, context):
    keyboard = []
    for group_name in context.bot_data["groups"]:
        keyboard.append([InlineKeyboardButton(group_name, callback_data=group_name)])
    text = "Pick a group's base to edit"

    update.callback_query.message.chat.send_message(text, reply_markup=InlineKeyboardMarkup(keyboard))
    return ADMIN_MANUAL_UPDATE2
       
def admin_manual_update2(update, context):
    group_name = update.callback_query.data
    context.user_data['admin_manual_group'] = group_name
    text = f"How much health would you like to add/Subtract from {group_name}?"
    update.callback_query.message.chat.send_message(text)
    return ADMIN_MANUAL_UPDATE3
    
def admin_manual_update3(update, context):
    try:
        delta_health = int(update.message.text)
    except ValueError:
        update.message.reply_text("Invalid number!!!! :((")
        return ADMIN_MENU
    
    context.user_data['admin_delta_health'] = delta_health
    group_name = context.user_data['admin_manual_group']

    text = f"What's the reason for adding {delta_health} health for {group_name}?"
    update.message.reply_text(text)
    return ADMIN_MANUAL_UPDATE4
    
def admin_manual_update4(update, context):
    delta_health = context.user_data['admin_delta_health']
    reason_msg = update.message.text
    
    # Send feedback to admin
    group_name = context.user_data['admin_manual_group']
    text = f"Added {delta_health} to {group_name}"
    update.message.reply_text(text)
        
    context.bot_data['groups'][group_name].health += delta_health
    group_final_health = context.bot_data['groups'][group_name].health

    # Send announcement to participants' group
    text = (
        f"{group_name}'s group has {'added' if delta_health > 0 else 'lost'} {delta_health} health!\n"
        f"Reason: {reason_msg}"
        f"They now have {group_final_health} health."
    )   
    context.bot.send_message(CHAT_PARTICIPANTS, text)
    return ADMIN_MENU

def admin_arena_status(update, context):
    text = "ADMIN ARENA STATUS\n"
    for group_name in context.bot_data["groups"]:
        # group will store all the key-value pairs in the dictionary
        group = context.bot_data["groups"][group_name]
        group_name = group.group_name
        group_health = group.health
        text += f"{group_name}: {group_health}\n"
    update.callback_query.message.chat.send_message(text)

# Choose which group to give
def admin_give_items(update, context):
    keyboard = []
    for group_name in context.bot_data["groups"]:
        keyboard.append([InlineKeyboardButton(group_name, callback_data=group_name)])

    text = "Pick a group to give the item to!"
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

    group = context.bot_data['groups'][group_name]
    group.items.append(item)

    update.callback_query.message.chat.send_message(text)

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
            CHOOSE_HERO: [
                CallbackQueryHandler(choose_hero_confirm, pattern='bat_girl'),
            ],
            USE_ITEMS: [
                CallbackQueryHandler(use_item2),
            ],
            BASE_DECLARE2: [
                MessageHandler(Filters.text, callback=base_declare2)
            ],
            BASE_DECLARE3: [
                MessageHandler(Filters.all, callback=base_declare3)
            ],
            ADMIN_MENU: [
                CallbackQueryHandler(arena_status, pattern='arena_status'),
                CallbackQueryHandler(admin_give_items, pattern='admin_give_items'),
                CallbackQueryHandler(admin_manual_update1, pattern='admin_manual_update'),
            ],
            ADMIN_MANUAL_UPDATE2: [
                CallbackQueryHandler(admin_manual_update2)
            ],
            ADMIN_MANUAL_UPDATE3:[
                MessageHandler(Filters.text, callback=admin_manual_update3)
            ],
            ADMIN_MANUAL_UPDATE4:[
                MessageHandler(Filters.text, callback=admin_manual_update4)
            ],
            ADMIN_GIVE_ITEM_NEXT: [
                # Will go to this function no matter which group is pressed
                CallbackQueryHandler(admin_give_items2),
            ],
            ADMIN_ITEM_CONFIRMATION: [
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

    # Populate fake data
    group1 = Group("team doggos", 12345)
    group2 = Group("team cats", 12345)
    dispatcher.bot_data['groups'] = { group.group_name: group for group in [group1, group2] }

    updater.start_polling()
    updater.idle()
