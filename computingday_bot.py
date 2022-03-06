import traceback

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

#from telegram.ext import pickle, DictPersistence

from keys import API_KEY, USER_ADMINS, CHAT_PARTICIPANTS, CHAT_ADMINS

# To assign each status to a number
_STATES = [
    'MAIN_MENU',
    'USE_ITEMS',
    'USE_ITEMS2',
    'REGISTER',
    'REGISTER_NAME',
    'REGISTER_NAME_CONFIRM',
    'BASE_DECLARE',
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
        self.using_potion = False
        



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
        context.user_data['using_item'] = None
        return admin_main_menu(update, context)

    # What users will receive
    text = "Welcome to Computing Day Mass Game! "
    update.message.reply_text(text)
    context.user_data["group"] = None
    print("Someone started the bot!")
    return main_menu(update, context)

# ====================  USER FUNCTIONS ====================

def menu(update, context):
    chat_id = update.effective_chat.id
    if chat_id in USER_ADMINS:
        return admin_main_menu(update, context)
    return main_menu(update, context)


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
    return MAIN_MENU


def status(update, context):
    group = context.user_data['group_name']
    text = ""
    for key, value in group.__dict__:
        text += f"{key}: {value} \n"
    update.message.reply_text(text)


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
    group = Group(group_name, update.effective_user.id)
    context.bot_data['groups'][group_name] = group
    context.user_data['group'] = group
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
    ]
    update.message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSE_HERO


def choose_hero_confirm(update, context):
    hero = update.callback_query.data
    group = context.user_data['group']
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
    try:
        context.bot.send_photo(
            CHAT_ADMINS,
            photo=update.message.photo[-1].file_id,
            caption=(
                f"Received from group: {group.group_name}\n"
                f"Base located at: {group.base}"
            )
        )
    except IndexError:
        print("ErroR!!!")
        print(dir(update.message))

    return MAIN_MENU


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
    for group in context.bot_data["groups"].values():
        if group.using_potion:
            continue
        keyboard.append([InlineKeyboardButton(group.group_name, callback_data=group.group_name)])
    
    text = f"Which group to use the {item} on?"
    update.callback_query.message.chat.send_message(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return USE_ITEMS2


def use_item_done(update, context):
    group = context.user_data['group']
    item = context.user_data['using_item']

    # Send what happened in participants group
    if item in ITEMS_OFFENSIVE:
        damage = ITEMS_OFFENSIVE[item]
        group.health -= damage
        text = (f"Someone has attacked {group.group_name}'s base using {item}!\n"
               f"{group.group_name}'s base is now {group.health}"
        )
        
    elif item in ITEMS_DEFENSIVE:
        text = f"{group.group_name}'s base has just used {item}!\n"
       if item == "potion":
            group.using_potion = True
            text += f"{group.group_name} is invulnerable for 5 minutes!"
            
            def potion_expired(context):
                group.using_potion = False
                
                text = f"Tick tock, 5 minutes is up! {group.group_name}'s potion effect has subsided. They are now vulnerable!"
                context.bot.send_message(CHAT_PARTICIPANTS, text)
                context.bot.send_message(CHAT_ADMINS, text)

            context.job_queue.run_once(potion_expired, 15)

        elif item == "base_mover":
            text += f"{group.group_name} has just shifted their base to an unknown location. Good luck finding!"
        
    context.bot.send_message(CHAT_PARTICIPANTS, text)
    context.bot.send_message(CHAT_ADMINS, text)
    
    return MAIN_MENU

# ==================== ADMIN FUNCTIONS ====================
def admin_main_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("Arena status", callback_data='arena_status'), ],
        [InlineKeyboardButton(
            "Give items", callback_data='admin_give_items'), ],
        [InlineKeyboardButton(
            "Manual Updates", callback_data='admin_manual_update'), ],
    ]
    text = "Welcome to the admin menu! Choose an action!"
    update.message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard))
    return ADMIN_MENU


def admin_manual_update1(update, context):
    keyboard = []
    for group_name in context.bot_data["groups"]:
        keyboard.append([InlineKeyboardButton(
            group_name, callback_data=group_name)])
    text = "Pick a group's base to edit"

    update.callback_query.message.chat.send_message(
        text, reply_markup=InlineKeyboardMarkup(keyboard))
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
    context.bot.send_message(CHAT_ADMINS, text)
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
        keyboard.append([InlineKeyboardButton(
            group_name, callback_data=group_name)])

    text = "Pick a group to give the item to!"
    update.callback_query.message.chat.send_message(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )
    # Reply to the query that the user sent
    return ADMIN_GIVE_ITEM_NEXT


# Choose which item to give to the group
def admin_give_items2(update, context):

    group_name = update.callback_query.data
    print("-------------------------------")
    print(group_name)
    context.user_data['admin_giveitem_group'] = group_name

    text = f"Pick an item to give {group_name}!"
    keyboard = []
    for item in ITEMS_OFFENSIVE:
        keyboard.append([InlineKeyboardButton(item, callback_data=item)])

    for item in ITEMS_DEFENSIVE:
        keyboard.append([InlineKeyboardButton(item, callback_data=item)])

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


def err(update, context):
    """Error handler callback for dispatcher"""
    error = context.error
    traceback.print_exception(error)
    if update is not None and update.effective_user is not None:
        context.bot.send_message(update.effective_user.id,
            "I'm sorry, an error has occurred. The devs have been alerted!"
        )


if __name__ == '__main__':
    top_conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            # current status: whatisreceivedfromuser(function to be called, pattern  = 'callback_data')
            MAIN_MENU: [
                CallbackQueryHandler(arena_status, pattern='arena_status'),
                CallbackQueryHandler(register, pattern='register'),
                CallbackQueryHandler(rules, pattern='rules'),
                CallbackQueryHandler(status, pattern='status'),
                CallbackQueryHandler(use_item, pattern='use_items'),
            ],
            REGISTER_NAME: [
                MessageHandler(Filters.text, callback=confirm_register),
            ],
            REGISTER_NAME_CONFIRM: [
                MessageHandler(Filters.regex("Yes"), callback=register_done),
                MessageHandler(Filters.regex("No"), callback=register_change),
            ],
            CHOOSE_HERO: [
                CallbackQueryHandler(choose_hero_confirm),
            ],
            BASE_DECLARE2: [
                MessageHandler(Filters.text, callback=base_declare2)
            ],
            BASE_DECLARE3: [
                MessageHandler(Filters.all, callback=base_declare3)
            ],
            USE_ITEMS: [
                CallbackQueryHandler(use_item2),
            ],
            USE_ITEMS2: [
                CallbackQueryHandler(use_item_done),
            ],
            ADMIN_MENU: [
                CallbackQueryHandler(arena_status, pattern='arena_status'),
                CallbackQueryHandler(
                    admin_give_items, pattern='admin_give_items'),
                CallbackQueryHandler(admin_manual_update1,
                                     pattern='admin_manual_update'),
            ],
            ADMIN_MANUAL_UPDATE2: [
                CallbackQueryHandler(admin_manual_update2)
            ],
            ADMIN_MANUAL_UPDATE3: [
                MessageHandler(Filters.text, callback=admin_manual_update3)
            ],
            ADMIN_MANUAL_UPDATE4: [
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
            CommandHandler('menu', callback=menu)
        ]
    )

    updater = Updater(API_KEY)
    dispatcher = Updater(API_KEY)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(top_conv)
    # dispatcher.add_error_handler(err)

    # Populate fake data
    group1 = Group("team doggos", 200)
    group2 = Group("team cats", 200)
    dispatcher.bot_data['groups'] = {
        group.group_name: group for group in [group1, group2]}
    dispatcher.user_data[273343228] = {
        'group': group1
    }

    updater.start_polling()
    updater.idle()
