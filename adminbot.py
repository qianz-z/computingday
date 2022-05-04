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
    MENU_ADMIN,
    ADMIN_GIVE_ITEM_NEXT,
    ADMIN_ITEM_CONFIRMATION,
    ADMIN_MANUAL_UPDATE2,
    ADMIN_MANUAL_UPDATE3,
    ADMIN_MANUAL_UPDATE4,
)
from const import (
    ITEMS_OFFENSIVE,
    ITEMS_DEFENSIVE,
)
from keys import CHAT_PARTICIPANTS, CHAT_ADMINS

def admin_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("Arena status", callback_data='arena_status')],
        [InlineKeyboardButton("Give items", callback_data='admin_give_items')],
        [InlineKeyboardButton("Manual Updates", callback_data='admin_manual_update')],
    ]
    text = "Welcome to the admin menu! Choose an action!"
    update.message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard))
    return MENU_ADMIN


def admin_manual_update1(update, context):
    keyboard = []
    for group_name in context.bot_data['groups']:
        keyboard.append([InlineKeyboardButton(group_name, callback_data=group_name)])
    text = "Pick a group's base to edit"

    update.callback_query.message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard))
    return ADMIN_MANUAL_UPDATE2


def admin_manual_update2(update, context):
    group_name = update.callback_query.data
    context.user_data['admin_manual_group'] = group_name
    text = f"How much health would you like to add/Subtract from {group_name}?"
    update.callback_query.message.reply_text(text)
    return ADMIN_MANUAL_UPDATE3


def admin_manual_update3(update, context):
    try:
        delta_health = int(update.message.text)
    except ValueError:
        update.message.reply_text("Invalid number!!!! :((")
        return MENU_ADMIN

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
    return MENU_ADMIN

update_conv = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            admin_manual_update1, pattern='admin_manual_update'),
    ],
    states={
        ADMIN_MANUAL_UPDATE2: [
            CallbackQueryHandler(admin_manual_update2)
        ],
        ADMIN_MANUAL_UPDATE3: [
            MessageHandler(Filters.text, callback=admin_manual_update3)
        ],
        ADMIN_MANUAL_UPDATE4: [
            MessageHandler(Filters.text, callback=admin_manual_update4)
        ],
    },
    fallbacks=[],
    allow_reentry=False,
    name='update_conv',
    persistent=True
)

def admin_arena_status(update, context):
    text = "ADMIN ARENA STATUS\n"
    for group_name in context.bot_data['groups']:
        # group will store all the key-value pairs in the dictionary
        group = context.bot_data['groups'][group_name]
        group_name = group.group_name
        group_health = group.health
        text += f"{group_name}: {group_health}\n"
    update.callback_query.message.reply_text(text)

# Choose which group to give


def admin_give_items(update, context):
    keyboard = []
    for group_name in context.bot_data['groups']:
        keyboard.append([InlineKeyboardButton(
            group_name, callback_data=group_name)])

    text = "Pick a group to give the item to!"
    update.callback_query.message.reply_text(
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
    for item in list(ITEMS_OFFENSIVE.keys()) + ITEMS_DEFENSIVE:
        keyboard.append([InlineKeyboardButton(item, callback_data=item)])

    update.callback_query.message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ADMIN_ITEM_CONFIRMATION


def admin_give_items3(update, context):
    # Getting the answer from callback_data in the prev function
    item = update.callback_query.data
    group_name = context.user_data['admin_giveitem_group']

    text = f"You've given {group_name} the item: {item}"

    group = context.bot_data['groups'][group_name]
    print("giving item to group with obj id ", id(group))
    group.items.append(item)

    update.callback_query.message.reply_text(text)

    return ConversationHandler.END


give_item_conv = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            admin_give_items, pattern='admin_give_items'),
    ],
    states={
        ADMIN_GIVE_ITEM_NEXT: [
            # Will go to this function no matter which group is pressed
            CallbackQueryHandler(admin_give_items2),
        ],
        ADMIN_ITEM_CONFIRMATION: [
            CallbackQueryHandler(admin_give_items3),
        ]
    },
    fallbacks=[],
    name='give_item_conv',
    persistent=True
)
